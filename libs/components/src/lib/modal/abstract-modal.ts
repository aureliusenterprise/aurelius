import { Input, OnDestroy, Output, ViewChild, Directive } from '@angular/core';
import { ModalComponent } from './modal.component';

@Directive()
export abstract class AbstractModal implements OnDestroy {
  /** The modal window. Inheriting components should always include a single `ModalComponent` */
  @ViewChild(ModalComponent, { static: true })
  protected readonly modal: ModalComponent;

  ngOnDestroy() {}

  /** Opens the modal form */
  activate() {
    this.modal.activate();
  }

  /** Closes the modal form */
  close() {
    this.modal.deactivate();
  }

  /** Returns an `Observable` stream of whether or not the modal is currently opened */
  get isActive() {
    return this.modal.isActive;
  }

  /** Set whether or not the form is open dynamically */
  @Input()
  set active(state: boolean) {
    this.modal.active = state;
  }

  /** Emits whenever the form closes or opens */
  @Output()
  get activeStateChanged() {
    return this.modal.activeStateChanged;
  }

  /** Emits whenever the form is closed */
  @Output()
  get closed() {
    return this.modal.cancelled;
  }
}
