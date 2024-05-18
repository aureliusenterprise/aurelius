import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { TranslateModule } from '@ngx-translate/core';
import { ConflictDetailsComponent } from './conflict-list/conflict-details/conflict-details.component';
import { ConflictListComponent } from './conflict-list/conflict-list.component';
import { ConflictResolutionRoutingModule } from './conflict-resolution-routing.module';
import { ConflictResolutionComponent } from './conflict-resolution.component';
import { ConflictResolutionGuard } from './conflict-resolution.guard';
import { ConflictResolutionService } from './conflict-resolution.service';
import { ScrollingModule } from '@angular/cdk/scrolling';
import { ProjectPermissionModule } from '@models4insight/permissions';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';

@NgModule({
  imports: [
    CommonModule,
    FontAwesomeModule,
    FormsModule,
    TranslateModule,
    ScrollingModule,
    ConflictResolutionRoutingModule,
    ReactiveFormsModule,
    ProjectPermissionModule
  ],
  declarations: [ConflictResolutionComponent, ConflictListComponent, ConflictDetailsComponent],
  providers: [ConflictResolutionGuard, ConflictResolutionService]
})
export class ConflictResolutionModule {}
