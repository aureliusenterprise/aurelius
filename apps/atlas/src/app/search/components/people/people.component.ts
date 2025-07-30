import { Component, Input, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { faUser } from '@fortawesome/free-solid-svg-icons';
import { AtlasEntityWithEXTInformation } from '@models4insight/atlas/api';
import { Observable } from 'rxjs';
import { map, tap } from 'rxjs/operators';
import { EntityDetailsService } from '../../services/entity-details/entity-details.service';

@Component({
  selector: 'models4insight-people',
  templateUrl: './people.component.html',
  styleUrls: ['./people.component.scss']
})
export class PeopleComponent implements OnInit {
  readonly personsIcon = faUser;

  details$: Observable<AtlasEntityWithEXTInformation>;
  noPeople$: Observable<boolean>;

  @Input() showPlaceholder = true;

  constructor(
    private readonly entityDetailsService: EntityDetailsService,
    private readonly router: Router
  ) {}

  ngOnInit() {
    this.details$ = this.entityDetailsService.select('entityDetails').pipe(
    tap(details => {
      console.log('Entity details:', details);
      console.log('Business owners:', details?.entity?.relationshipAttributes?.businessOwner);
    })
  );
    this.noPeople$ = this.entityDetailsService
      .select(['entityDetails', 'entity', 'relationshipAttributes'])
      .pipe(
        map(relationshipAttributes => {
          const people = [
            ...(relationshipAttributes.domainLead || []),
            ...(relationshipAttributes.businessOwner || []),
            ...(relationshipAttributes.steward || [])
          ];

          return people.length === 0;
        })
      );
  }

  deduplicate(items: any[]): any[] {
    console.log('Items to deduplicate:', items);

    if (!items) return [];

    const uniqueItems = new Map();
    items.forEach(item => {
      console.log('Processing item:', item);
      // The items are already the person objects, no need to access [0]
      if (item && !uniqueItems.has(item.guid)) {
        uniqueItems.set(item.guid, item);
      }
    });

  const result = Array.from(uniqueItems.values());
  console.log('Deduplicated result:', result);
  return result;
}
}
