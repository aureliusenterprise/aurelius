import { Component, OnInit } from '@angular/core';
import { faFilter } from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'models4insight-relationships-facets',
  templateUrl: 'relationships-facets.component.html',
  styleUrls: ['relationships-facets.component.scss']
})
export class RelationshipsFacetsComponent implements OnInit {
  readonly faFilter = faFilter;

  constructor() {}

  ngOnInit() {}

  preventBlur(event: Event) {
    event.preventDefault();
  }
}
