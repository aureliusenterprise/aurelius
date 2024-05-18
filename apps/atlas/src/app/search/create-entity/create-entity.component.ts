import { Component, OnInit } from '@angular/core';
import { AtlasEntityWithEXTInformation } from '@models4insight/atlas/api';
import { v4 as uuid } from 'uuid';
import { EntityDetailsService } from '../services/entity-details/entity-details.service';
import { generatePlaceholderId } from '../utils';

@Component({
  selector: 'models4insight-create-entity',
  templateUrl: './create-entity.component.html',
  styleUrls: ['./create-entity.component.scss'],
  providers: [EntityDetailsService],
})
export class CreateEntityComponent implements OnInit {
  constructor(private readonly entityDetailsService: EntityDetailsService) {}

  ngOnInit(): void {
    this.resetEditor();
  }

  private resetEditor() {
    const entityDetails: AtlasEntityWithEXTInformation = {
      entity: {
        guid: generatePlaceholderId(),
        attributes: {
          qualifiedName: uuid(),
        },
        relationshipAttributes: {},
        classifications: [],
        typeName: null,
      },
      referredEntities: {},
    };

    this.entityDetailsService.set({
      description: 'Create entity reset',
      payload: {
        entityDetails,
      },
    });
  }
}
