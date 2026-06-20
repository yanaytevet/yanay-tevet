import {Component, computed, inject, signal} from '@angular/core';
import {NgClass} from '@angular/common';
import {ActivatedRoute} from '@angular/router';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {
  featherArrowLeft,
  featherChevronLeft,
  featherChevronRight,
  featherUserPlus,
} from '@ng-icons/feather-icons';
import {
  getRentalProjectView,
  getUnitCalendarView,
  listUnitsView,
  paginateVillaVillekullaProjectsView,
  RentalProjectSchema,
  UnitBookingSchema,
  UnitSchema,
} from '../../../../generated-files/api/villa-villekulla';
import {AuthenticationService} from '../../../common/authentication/authentication.service';
import {DialogService} from '../../../common/dialogs/dialogs.service';
import {RoutingService} from '../../../shared/services/routing.service';
import {VillaBookingDialogComponent} from '../villa-booking-dialog/villa-booking-dialog.component';
import {VillaBookingDetailsDialogComponent} from '../villa-booking-details-dialog/villa-booking-details-dialog.component';
import {VillaInviteDialogComponent} from '../villa-invite-dialog/villa-invite-dialog.component';

interface DayCell {
  iso: string;
  dayNum: number;
  inMonth: boolean;
  isPast: boolean;
  isToday: boolean;
  booking: UnitBookingSchema | null;
  mine: boolean;
  showLabel: boolean;
  label: string;
  disabled: boolean;
  classes: string;
}

function toIso(date: Date): string {
  const year = date.getFullYear();
  const month = `${date.getMonth() + 1}`.padStart(2, '0');
  const day = `${date.getDate()}`.padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function cellClasses(inMonth: boolean, isPast: boolean, booking: UnitBookingSchema | null, mine: boolean): string {
  const parts: string[] = [];
  if (!inMonth) {
    parts.push('opacity-40');
  }
  if (booking === null) {
    parts.push('border-transparent');
    if (isPast) {
      parts.push('bg-layer-1', 'text-writing-least');
    } else {
      parts.push('bg-layer-2', 'hover:bg-layer-3', 'cursor-pointer');
    }
  } else if (mine) {
    parts.push('bg-notion-blue/15', 'border-notion-blue/40', 'cursor-pointer');
  } else {
    parts.push('bg-layer-4', 'border-layer-4', 'cursor-pointer');
  }
  return parts.join(' ');
}

@Component({
  selector: 'app-villa-calendar',
  standalone: true,
  imports: [NgIcon, NgClass],
  providers: [provideIcons({featherArrowLeft, featherChevronLeft, featherChevronRight, featherUserPlus})],
  templateUrl: './villa-calendar.component.html',
})
export class VillaCalendarComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly authService = inject(AuthenticationService);
  private readonly dialogService = inject(DialogService);
  private readonly routingService = inject(RoutingService);

  readonly isLoading = signal<boolean>(true);
  readonly loadError = signal<string | null>(null);
  readonly project = signal<RentalProjectSchema | null>(null);
  readonly unit = signal<UnitSchema | null>(null);
  readonly bookings = signal<UnitBookingSchema[]>([]);
  readonly canManageAll = signal<boolean>(false);
  readonly showBack = signal<boolean>(false);
  readonly viewMonth = signal<Date>(this.startOfMonth(new Date()));

  private readonly todayIso = toIso(new Date());

  readonly monthLabel = computed<string>(() =>
    this.viewMonth().toLocaleDateString(undefined, {month: 'long', year: 'numeric'}),
  );

  readonly weekdayLabels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  readonly cells = computed<DayCell[]>(() => {
    const month = this.viewMonth();
    const userId = this.authService.user()?.id ?? null;
    const bookingByIso = new Map<string, UnitBookingSchema>();
    for (const booking of this.bookings()) {
      const cursor = new Date(`${booking.start_date}T00:00:00`);
      const end = new Date(`${booking.end_date}T00:00:00`);
      while (cursor < end) {
        bookingByIso.set(toIso(cursor), booking);
        cursor.setDate(cursor.getDate() + 1);
      }
    }
    const firstCell = new Date(month);
    firstCell.setDate(1 - month.getDay());
    const result: DayCell[] = [];
    for (let i = 0; i < 42; i++) {
      const date = new Date(firstCell);
      date.setDate(firstCell.getDate() + i);
      const iso = toIso(date);
      const booking = bookingByIso.get(iso) ?? null;
      const inMonth = date.getMonth() === month.getMonth();
      const isPast = iso < this.todayIso;
      const mine = booking !== null && userId !== null && booking.created_by_id === userId;
      const prev = result[i - 1];
      const isSegmentStart = booking !== null && (i % 7 === 0 || !prev || prev.booking?.id !== booking.id);
      result.push({
        iso,
        dayNum: date.getDate(),
        inMonth,
        isPast,
        isToday: iso === this.todayIso,
        booking,
        mine,
        showLabel: isSegmentStart,
        label: booking === null ? '' : mine ? 'You' : booking.created_by_name || 'Booked',
        disabled: isPast && booking === null,
        classes: cellClasses(inMonth, isPast, booking, mine),
      });
    }
    return result;
  });

  protected readonly featherArrowLeft = featherArrowLeft;
  protected readonly featherChevronLeft = featherChevronLeft;
  protected readonly featherChevronRight = featherChevronRight;
  protected readonly featherUserPlus = featherUserPlus;

  constructor() {
    this.route.paramMap.subscribe(params => {
      const idStr = params.get('id');
      if (idStr) {
        void this.load(Number(idStr));
      }
    });
  }

  private startOfMonth(date: Date): Date {
    return new Date(date.getFullYear(), date.getMonth(), 1);
  }

  private async load(projectId: number): Promise<void> {
    this.isLoading.set(true);
    this.loadError.set(null);
    try {
      const [projectRes, unitsRes, projectsRes] = await Promise.all([
        getRentalProjectView({path: {object_id: projectId}}),
        listUnitsView({path: {object_id: projectId}}),
        paginateVillaVillekullaProjectsView({query: {page: 0, page_size: 50}}),
      ]);
      this.project.set(projectRes.data);
      const unit = unitsRes.data.units[0] ?? null;
      this.unit.set(unit);
      const isSiteAdmin = this.authService.user()?.is_admin ?? false;
      this.showBack.set(isSiteAdmin || projectsRes.data.data.length > 1);
      if (unit !== null) {
        await this.loadCalendar(unit.id);
      }
    } catch {
      this.loadError.set('Could not load this property. You may not have access to it.');
    } finally {
      this.isLoading.set(false);
    }
  }

  private async loadCalendar(unitId: number): Promise<void> {
    const res = await getUnitCalendarView({path: {unit_id: unitId}});
    this.bookings.set(res.data.bookings);
    this.canManageAll.set(res.data.can_manage_all);
  }

  prevMonth(): void {
    const month = this.viewMonth();
    this.viewMonth.set(new Date(month.getFullYear(), month.getMonth() - 1, 1));
  }

  nextMonth(): void {
    const month = this.viewMonth();
    this.viewMonth.set(new Date(month.getFullYear(), month.getMonth() + 1, 1));
  }

  async back(): Promise<void> {
    await this.routingService.navigateToVillaVillekulla();
  }

  async onDayClick(cell: DayCell): Promise<void> {
    if (cell.booking !== null) {
      await this.openBooking(cell.booking, cell.mine);
      return;
    }
    if (cell.isPast) {
      return;
    }
    const unit = this.unit();
    if (unit === null) {
      return;
    }
    const created = await this.dialogService.open<
      {unitId: number; defaultStart: string; bookings: UnitBookingSchema[]},
      UnitBookingSchema
    >(
      VillaBookingDialogComponent,
      {unitId: unit.id, defaultStart: cell.iso, bookings: this.bookings()},
      45,
    );
    if (created !== null) {
      await this.loadCalendar(unit.id);
    }
  }

  private async openBooking(booking: UnitBookingSchema, mine: boolean): Promise<void> {
    const unit = this.unit();
    if (unit === null) {
      return;
    }
    if (!mine && !this.canManageAll()) {
      await this.dialogService.showNotificationDialog({
        title: 'Booked',
        text: `These dates are taken (${booking.start_date} → ${booking.end_date}).`,
      });
      return;
    }
    const changed = await this.dialogService.open<{booking: UnitBookingSchema}, boolean>(
      VillaBookingDetailsDialogComponent,
      {booking},
      45,
    );
    if (changed) {
      await this.loadCalendar(unit.id);
    }
  }

  async openInvite(): Promise<void> {
    const project = this.project();
    if (project === null) {
      return;
    }
    await this.dialogService.open<{projectId: number}, null>(
      VillaInviteDialogComponent,
      {projectId: project.id},
      45,
    );
  }
}
