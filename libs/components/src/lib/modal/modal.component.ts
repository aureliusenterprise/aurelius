import {
  Component,
  EventEmitter,
  Input,
  OnDestroy,
  OnInit,
  Output,
} from '@angular/core';
import { untilDestroyed } from '@models4insight/utils';
import { BehaviorSubject, Observable } from 'rxjs';
import { distinctUntilChanged } from 'rxjs/operators';

export interface ModalContext {
  cancel: string;
  closeOnConfirm: boolean;
  confirm?: string;
  title: string;
}

export const defaultModalContext: ModalContext = {
  cancel: 'Close',
  closeOnConfirm: true,
  confirm: 'Save',
  title: 'Title',
};

@Component({
  selector: 'models4insight-modal',
  templateUrl: 'modal.component.html',
  styleUrls: ['modal.component.scss'],
})
export class ModalComponent implements OnInit, OnDestroy {
  /** Defines the behavior of the modal dialog, such as button text and title */
  @Input() context: ModalContext = defaultModalContext;
  /** Whether or not the confirm button should show a loading spinner */
  @Input() isLoading = false;

  /** Emits whenever the modal opens or closes */
  @Output() readonly activeStateChanged = new EventEmitter<boolean>();
  /** Emits whenever the modal is cancelled */
  @Output() readonly cancelled = new EventEmitter<void>();
  /** Emits whenever the modal is confirmed */
  @Output() readonly confirmed = new EventEmitter<void>();

  /** Indicates whether or not the modal is currently opened */
  private isActive$: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(
    false
  );

  ngOnInit() {
    // Whenever the active state changes, trigger an event that can be consumed by the parent component.
    this.isActive$
      .pipe(distinctUntilChanged(), untilDestroyed(this))
      .subscribe(this.activeStateChanged);
  }

  ngOnDestroy() {}

  /** Opens the modal window */
  activate() {
    this.isActive$.next(true);
  }

  /** Triggers a cancelled event and closes the modal window */
  cancel() {
    this.cancelled.emit();
    this.deactivate();
  }

  /** Triggers a confirmed event and closes the modal window if so configured */
  confirm() {
    this.confirmed.emit();
    if (this.context.closeOnConfirm) {
      this.deactivate();
    }
  }

  /** Closes the modal window */
  deactivate() {
    this.isActive$.next(false);
  }

  /** Dynamically opens or closes the modal based on an outside source */
  @Input()
  set active(state: boolean) {
    this.isActive$.next(state);
  }

  /** Returns an observable stream of whether or not the modal is currently opened */
  get isActive(): Observable<boolean> {
    return this.isActive$.asObservable();
  }
}
