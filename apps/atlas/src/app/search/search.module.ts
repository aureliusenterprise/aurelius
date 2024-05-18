import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import {
  AppSearchService,
  AtlasEntitySearchService
} from '@models4insight/atlas/api';
import {
  HeroModule,
  SimpleSearchInputModule
} from '@models4insight/components';
import { KeycloakRolePermissionModule } from '@models4insight/permissions';
import { BrowseModule } from './browse/browse.module';
import { CreateEntityModule } from './create-entity/create-entity.module';
import { EditEntityModule } from './edit-entity/edit-entity.module';
import { ResultsModule } from './results/results.module';
import { SearchRoutingModule } from './search-routing.module';
import { SearchComponent } from './search.component';
import { EntitySearchService } from './services/search/entity-search.service';
import { SearchService } from './services/search/search.service';

@NgModule({
  declarations: [SearchComponent],
  imports: [
    CommonModule,
    SimpleSearchInputModule,
    FontAwesomeModule,
    HeroModule,
    ResultsModule,
    BrowseModule,
    KeycloakRolePermissionModule,
    SearchRoutingModule,
    CreateEntityModule,
    EditEntityModule,
  ],
  providers: [
    EntitySearchService,
    { provide: SearchService, useExisting: EntitySearchService },
    { provide: AppSearchService, useClass: AtlasEntitySearchService },
  ],
})
export class SearchModule {}
