import {Component, computed, inject, signal} from '@angular/core';
import {NgClass} from '@angular/common';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {
  featherChevronLeft,
  featherChevronRight,
  featherPlus,
  featherUserPlus,
} from '@ng-icons/feather-icons';
import {
  createVillaVillekullaProjectView,
  deleteUnitBookingView,
  listProjectMembersView,
  listUnitsView,
  paginateUnitBookingsView,
  paginateVillaVillekullaProjectsView,
  RentalProjectSchema,
  UnitBookingSchema,
  UnitSchema,
} from '../../../generated-files/api/villa-villekulla';
import {AuthenticationService} from '../../common/authentication/authentication.service';
import {DialogService} from '../../common/dialogs/dialogs.service';
import {VillaBookingDialogComponent} from './villa-booking-dialog/villa-booking-dialog.component';
import {VillaInviteDialogComponent} from './villa-invite-dialog/villa-invite-dialog.component';

interface DayCell {
  iso: string;
  dayNum: number;
  inMonth: boolean;
  isPast: boolean;
  isToday: boolean;
  booking: UnitBookingSchema | null;
  isBookingStart: boolean;
  bookerName: string;
  mine: boolean;
  disabled: boolean;
  classes: string;
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

function toIso(date: Date): string {
  const year = date.getFullYear();
  const month = `${date.getMonth() + 1}`.padStart(2, '0');
  const day = `${date.getDate()}`.padStart(2, '0');
  return `${year}-${month}-${day}`;
}

@Component({
  selector: 'app-villa-villekulla',
  standalone: true,
  imports: [NgIcon, NgClass],
  providers: [provideIcons({featherChevronLeft, featherChevronRight, featherPlus, featherUserPlus})],
  templateUrl: './villa-villekulla.component.html',
})
export class VillaVillekullaComponent {
  private readonly authService = inject(AuthenticationService);
  private readonly dialogService = inject(DialogService);

  readonly isLoading = signal<boolean>(true);
  readonly project = signal<RentalProjectSchema | null>(null);
  readonly unit = signal<UnitSchema | null>(null);
  readonly bookings = signal<UnitBookingSchema[]>([]);
  readonly myRole = signal<string | null>(null);
  readonly viewMonth = signal<Date>(this.startOfMonth(new Date()));

  private readonly todayIso = toIso(new Date());

  readonly isSiteAdmin = computed<boolean>(() => this.authService.user()?.is_admin ?? false);
  readonly canManage = computed<boolean>(() => this.isSiteAdmin() || this.myRole() === 'owner');

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
      result.push({
        iso,
        dayNum: date.getDate(),
        inMonth,
        isPast,
        isToday: iso === this.todayIso,
        booking,
        isBookingStart: booking !== null && booking.start_date === iso,
        bookerName: booking?.created_by_name ?? '',
        mine,
        disabled: isPast && booking === null,
        classes: cellClasses(inMonth, isPast, booking, mine),
      });
    }
    return result;
  });

  protected readonly featherChevronLeft = featherChevronLeft;
  protected readonly featherChevronRight = featherChevronRight;
  protected readonly featherPlus = featherPlus;
  protected readonly featherUserPlus = featherUserPlus;

  constructor() {
    void this.init();
  }

  private startOfMonth(date: Date): Date {
    return new Date(date.getFullYear(), date.getMonth(), 1);
  }

  private async init(): Promise<void> {
    this.isLoading.set(true);
    try {
      const projectsRes = await paginateVillaVillekullaProjectsView({query: {page: 0, page_size: 50}});
      const projects = projectsRes.data.data;
      if (projects.length === 0) {
        this.project.set(null);
        return;
      }
      await this.selectProject(projects[0]);
    } finally {
      this.isLoading.set(false);
    }
  }

  private async selectProject(project: RentalProjectSchema): Promise<void> {
    this.project.set(project);
    const [unitsRes, membersRes] = await Promise.all([
      listUnitsView({path: {object_id: project.id}}),
      listProjectMembersView({path: {object_id: project.id}}),
    ]);
    const me = this.authService.user()?.id ?? null;
    const myMembership = membersRes.data.members.find(m => m.user_id === me);
    this.myRole.set(myMembership?.role ?? null);
    const unit = unitsRes.data.units[0] ?? null;
    this.unit.set(unit);
    if (unit !== null) {
      await this.loadBookings(unit.id);
    }
  }

  private async loadBookings(unitId: number): Promise<void> {
    const res = await paginateUnitBookingsView({path: {unit_id: unitId}, query: {page: 0, page_size: 500}});
    this.bookings.set(res.data.data);
  }

  prevMonth(): void {
    const month = this.viewMonth();
    this.viewMonth.set(new Date(month.getFullYear(), month.getMonth() - 1, 1));
  }

  nextMonth(): void {
    const month = this.viewMonth();
    this.viewMonth.set(new Date(month.getFullYear(), month.getMonth() + 1, 1));
  }

  async onDayClick(cell: DayCell): Promise<void> {
    if (cell.booking !== null) {
      await this.tryCancel(cell);
      return;
    }
    if (cell.isPast) {
      return;
    }
    const unit = this.unit();
    if (unit === null) {
      return;
    }
    const created = await this.dialogService.open<{unitId: number; defaultStart: string}, UnitBookingSchema>(
      VillaBookingDialogComponent,
      {unitId: unit.id, defaultStart: cell.iso},
      45,
    );
    if (created !== null) {
      await this.loadBookings(unit.id);
    }
  }

  private async tryCancel(cell: DayCell): Promise<void> {
    const booking = cell.booking;
    const unit = this.unit();
    if (booking === null || unit === null) {
      return;
    }
    if (!cell.mine && !this.canManage()) {
      await this.dialogService.showNotificationDialog({
        title: 'Booked',
        text: `These dates are booked by ${booking.created_by_name || 'someone else'}.`,
      });
      return;
    }
    const confirmed = await this.dialogService.getBooleanFromConfirmationDialog({
      title: 'Cancel booking',
      text: `Cancel the booking from ${booking.start_date} to ${booking.end_date}?`,
      confirmActionName: 'Cancel booking',
      cancelActionName: 'Keep',
    });
    if (!confirmed) {
      return;
    }
    try {
      await deleteUnitBookingView({path: {object_id: booking.id}});
      await this.loadBookings(unit.id);
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
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
    await this.selectProject(project);
  }

  async createProject(): Promise<void> {
    const name = await this.dialogService.getTextFromInputDialog({
      title: 'Create Villa Villekulla',
      text: 'Name this property. You can invite friends to book it once it exists.',
      label: 'Property name',
      defaultValue: 'Villa Villekulla',
      confirmActionName: 'Create',
    });
    if (!name) {
      return;
    }
    this.isLoading.set(true);
    try {
      const res = await createVillaVillekullaProjectView({body: {name}});
      await this.selectProject(res.data);
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
    } finally {
      this.isLoading.set(false);
    }
  }
}
