import { Component, OnDestroy, OnInit } from '@angular/core';
import { EntityDetailsService } from '../services/entity-details/entity-details.service';

@Component({
  selector: 'models4insight-edit-entity',
  templateUrl: './edit-entity.component.html',
  styleUrls: ['./edit-entity.component.scss']
})
export class EditEntityComponent implements OnInit, OnDestroy {

  constructor(private readonly entityDetailsService: EntityDetailsService) { }

  ngOnInit(): void {
  }

  ngOnDestroy(): void {
    this.entityDetailsService.clear();
  }

}
