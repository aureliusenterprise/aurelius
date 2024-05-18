import { Component, Input, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { faUser } from '@fortawesome/free-solid-svg-icons';
import { AtlasEntityWithEXTInformation } from '@models4insight/atlas/api';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
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
    this.details$ = this.entityDetailsService.select('entityDetails');
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

  directToDetailsPage(guid: string) {
    this.router.navigate(['search/details', guid]);
  }
}
