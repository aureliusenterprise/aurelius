import {
  Component,
  EventEmitter,
  OnDestroy,
  OnInit,
  Output,
} from '@angular/core';
import { UserSearch } from '@models4insight/repository';
import { untilDestroyed } from '@models4insight/utils';
import { UserSearchInputService } from './user-search-input.service';

@Component({
  selector: 'models4insight-user-search-input',
  templateUrl: 'user-search-input.component.html',
  styleUrls: ['user-search-input.component.scss'],
  providers: [UserSearchInputService],
})
export class UserSearchInputComponent implements OnInit, OnDestroy {
  @Output() suggestions: EventEmitter<UserSearch[]> = new EventEmitter<
    UserSearch[]
  >();

  constructor(private readonly searchService: UserSearchInputService) {}

  ngOnInit() {
    this.searchService
      .select('suggestions')
      .pipe(untilDestroyed(this))
      .subscribe(this.suggestions);
  }

  ngOnDestroy() {}

  searchForUsers(query: string) {
    this.searchService.update({
      description: 'New user search query available',
      payload: { query },
    });
  }
}
