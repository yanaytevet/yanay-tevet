import {Component, effect, input, output, signal, untracked} from '@angular/core';
import {NgClass} from '@angular/common';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {bootstrapChevronDown, bootstrapChevronUp, bootstrapGripVertical} from '@ng-icons/bootstrap-icons';
import {CdkDragDrop, DragDropModule, moveItemInArray} from '@angular/cdk/drag-drop';

export interface ReorderableListTag {
  text: string;
  color?: string;
}

export interface ReorderableListIconButton {
  svg: string;
  onClick: () => void;
  className?: string;
  title?: string;
}

export interface ReorderableListItem {
  id: string | number;
  text: string;
  description?: string;
  tags?: ReorderableListTag[];
  iconButtons?: ReorderableListIconButton[];
}

@Component({
  selector: 'app-reorderable-list',
  standalone: true,
  imports: [NgIcon, DragDropModule, NgClass],
  providers: [provideIcons({bootstrapChevronUp, bootstrapChevronDown, bootstrapGripVertical})],
  templateUrl: './reorderable-list.component.html',
})
export class ReorderableListComponent {
  items = input.required<ReorderableListItem[]>();
  emptyMessage = input<string>('No items yet.');
  disabled = input<boolean>(false);
  reordered = output<ReorderableListItem[]>();

  protected readonly bootstrapChevronUp = bootstrapChevronUp;
  protected readonly bootstrapChevronDown = bootstrapChevronDown;
  protected readonly bootstrapGripVertical = bootstrapGripVertical;

  protected localItems = signal<ReorderableListItem[]>([]);

  constructor() {
    effect(() => {
      const newItems = this.items();
      const current = untracked(() => this.localItems());
      // Skip re-render if IDs, text, description, and button counts are unchanged (e.g. after backend confirms a drag)
      if (current.length === newItems.length &&
          current.every((item, i) =>
            item.id === newItems[i].id &&
            item.text === newItems[i].text &&
            item.description === newItems[i].description &&
            (item.iconButtons?.length ?? 0) === (newItems[i].iconButtons?.length ?? 0) &&
            (item.tags?.length ?? 0) === (newItems[i].tags?.length ?? 0))) {
        return;
      }
      this.localItems.set([...newItems]);
    });
  }

  protected moveUp(index: number) {
    if (index === 0) {
      return;
    }
    const arr = [...this.localItems()];
    [arr[index - 1], arr[index]] = [arr[index], arr[index - 1]];
    this.localItems.set(arr);
    this.reordered.emit(arr);
  }

  protected moveDown(index: number) {
    if (index === this.localItems().length - 1) {
      return;
    }
    const arr = [...this.localItems()];
    [arr[index], arr[index + 1]] = [arr[index + 1], arr[index]];
    this.localItems.set(arr);
    this.reordered.emit(arr);
  }

  protected onDrop(event: CdkDragDrop<ReorderableListItem[]>) {
    const arr = [...this.localItems()];
    moveItemInArray(arr, event.previousIndex, event.currentIndex);
    this.localItems.set(arr);
    this.reordered.emit(arr);
  }
}
