import { Component, OnInit } from '@angular/core';
import { Dictionary } from 'lodash';
import { Observable } from 'rxjs';
import { ClassificationsListService } from './classifications-list.service';

@Component({
  selector: 'models4insight-classifications-list',
  templateUrl: 'classifications-list.component.html',
  styleUrls: ['classifications-list.component.scss'],
  providers: [ClassificationsListService]
})
export class ClassificationsListComponent implements OnInit {
  classificationsByTypeName$: Observable<Dictionary<string[]>>;

  constructor(
    private readonly classificationsListService: ClassificationsListService
  ) {}

  ngOnInit() {
    this.classificationsByTypeName$ = this.classificationsListService.state;
  }
}
