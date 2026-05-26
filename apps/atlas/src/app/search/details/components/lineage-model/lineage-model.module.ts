import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { Modelview2Module } from '@models4insight/modelview2';
import { DetailsCardModule } from '../../../components/cards/details-card.module';
import { LineageModelComponent } from './lineage-model.component';
import { ModelExplorerDataGovernanceComponent } from './model-explorer-data-governance/model-explorer-data-governance.component';
import { TranslateModule } from '@ngx-translate/core';

@NgModule({
    imports: [CommonModule, DetailsCardModule, FontAwesomeModule, Modelview2Module, TranslateModule],
    declarations: [LineageModelComponent, ModelExplorerDataGovernanceComponent],
    exports: [LineageModelComponent],
})
export class LineageModelModule {}
