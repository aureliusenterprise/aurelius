import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { TranslateModule } from '@ngx-translate/core';
import { ClassificationLabelModule } from '../../components/classification-label';
import { DatasetOverviewComponent } from './dataset-overview.component';

@NgModule({
    imports: [CommonModule, FormsModule, RouterModule, FontAwesomeModule, TranslateModule.forChild(), ClassificationLabelModule],
    declarations: [DatasetOverviewComponent],
    exports: [DatasetOverviewComponent],
})
export class DatasetOverviewModule {}
