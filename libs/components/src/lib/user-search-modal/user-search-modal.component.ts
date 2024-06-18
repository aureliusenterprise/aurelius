import {
  Component,
  EventEmitter,
  Input,
  OnDestroy,
  OnInit,
  Output,
  ViewChild,
} from '@angular/core';
import { UserSearch } from '@models4insight/repository';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { ModalComponent, ModalContext } from '../modal';
import { UserSearchInputComponent } from '../user-search-input';
import { faPlus } from '@fortawesome/free-solid-svg-icons';

const modalContext: ModalContext = {
  cancel: 'Close',
  closeOnConfirm: true,
  title: 'Add a new member to your project',
};

@Component({
  selector: 'models4insight-user-search-modal',
  templateUrl: 'user-search-modal.component.html',
  styleUrls: ['user-search-modal.component.scss'],
})
export class UserSearchModalComponent implements OnInit, OnDestroy {
  suggestedUsers$: Observable<UserSearch[]>;

  @Input() currentUsers: string[] = [];

  @Output() user: EventEmitter<UserSearch> = new EventEmitter<UserSearch>();

  faPlus = faPlus;

  @ViewChild(ModalComponent, { static: true })
  private readonly modal: ModalComponent;

  @ViewChild(UserSearchInputComponent, { static: true })
  private readonly searchInput: UserSearchInputComponent;

  ngOnInit() {
    this.modal.context = modalContext;
    this.suggestedUsers$ = this.searchInput.suggestions.pipe(
      map((suggestions) =>
        suggestions
          .filter(({ userName }) => !this.currentUsers.includes(userName))
          .slice(0, 5)
      )
    );
  }

  ngOnDestroy() {}

  activate() {
    this.modal.activate();
  }

  onAddMember(user: UserSearch) {
    this.user.emit(user);
    this.modal.confirm();
  }
}
