import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { SortableTableShellModule, ModalModule } from '@models4insight/components';
import { FeatureModule } from '@models4insight/permissions';
import { TranslateModule } from '@ngx-translate/core';
import { RulesRoutingModule } from './rules-routing.module';
import { RulesComponent } from './rules.component';
import { RulesService } from './rules.service';
import { SaveRulesModalComponent } from './save-rules-modal/save-rules-modal.component';

@NgModule({
  imports: [
    CommonModule,
    TranslateModule,
    RulesRoutingModule,
    FormsModule,
    SortableTableShellModule,
    ReactiveFormsModule,
    FeatureModule,
    FontAwesomeModule,
    ModalModule
  ],
  declarations: [RulesComponent, SaveRulesModalComponent],
  providers: [RulesService]
})
export class RulesModule {}
