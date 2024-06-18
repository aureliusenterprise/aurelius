import { Component, EventEmitter, Input, Output } from '@angular/core';
import { faThumbtack } from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'models4insight-quickview',
  templateUrl: 'quickview.component.html',
  styleUrls: ['quickview.component.scss'],
})
export class QuickviewComponent {
  /** Emits whenever the quickview is closed */
  @Output() readonly closed = new EventEmitter<void>();
  /** Emits whenever the quickview is opened */
  @Output() readonly opened = new EventEmitter<void>();

  readonly faThumbtack = faThumbtack;

  /**
   * Whether or not the quickview should stay open if `close()` is called.
   * You can ignore this setting by calling `close(true)`.
   */
  @Input() isPinned = false;

  /**
   * The text to show at the top of the quickview.
   */
  @Input() name = 'Details';

  /**
   * Whether or not the quickview is currently open.
   */
  isActive = false;

  /**
   * Close the quickview pane.
   * @param force Whether or not to close the quickview pane even if `this.isPinned` is `true`.
   */
  close(force: boolean) {
    if (this.isActive && (!this.isPinned || force)) {
      this.isActive = false;
      this.closed.emit();
    }
  }

  /**
   * Open the quickview pane.
   */
  open() {
    if (!this.isActive) {
      this.isActive = true;
      this.opened.emit();
    }
  }

  /**
   * Toggle whether or not the quickview is pinned.
   */
  toggleIsPinned() {
    this.isPinned = !this.isPinned;
  }
}
