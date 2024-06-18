import { Input, Output, ViewChild, Directive } from '@angular/core';
import { BaseComponent } from '../base-component';
import { QuickviewComponent } from './quickview.component';

@Directive()
export abstract class BaseQuickview extends BaseComponent {
  /**
   * Reference to the parent quickview
   */
  abstract quickview: QuickviewComponent;

  /**
   * Close the quickview pane.
   * @param force Whether or not to close the quickview pane even if `this.isPinned` is `true`.
   */
  close(force?: boolean) {
    this.quickview.close(force);
  }

  /**
   * Open the quickview pane.
   */
  open() {
    this.quickview.open();
  }

  /**
   * Toggle whether or not the quickview is pinned.
   */
  toggleIsPinned() {
    this.quickview.toggleIsPinned();
  }

  /**
   * Emits whenever the quickview is closed
   */
  @Output() get closed() {
    return this.quickview.closed;
  }

  /**
   * Emits whenever the quickview is opened
   */
  @Output() get opened() {
    return this.quickview.opened;
  }

  get isActive() {
    return this.quickview.isActive;
  }

  /**
   * Whether or not the quickview should stay open if `close()` is called.
   * You can ignore this setting by calling `close(true)`.
   */
  @Input() set isPinned(isPinned: boolean) {
    this.quickview.isPinned = isPinned;
  }

  get isPinned() {
    return this.quickview.isPinned;
  }

  /**
   * The text to show at the top of the quickview.
   */
  @Input() set name(title: string) {
    this.quickview.name = title;
  }

  get name() {
    return this.quickview.name;
  }
}
