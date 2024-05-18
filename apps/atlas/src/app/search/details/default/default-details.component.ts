import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { FilteredPropertiesService } from '../../services/filtered-properties/filtered-properties.service';

@Component({
  selector: 'models4insight-default-details',
  templateUrl: 'default-details.component.html',
  styleUrls: ['default-details.component.scss']
})
export class DefaultDetailsComponent implements OnInit {
  propertyCount$: Observable<number>;

  constructor(
    private readonly filteredPropertiesService: FilteredPropertiesService
  ) {}

  ngOnInit() {
    this.propertyCount$ = this.filteredPropertiesService.state.pipe(
      map(properties => Object.keys(properties).length)
    );
  }
}
