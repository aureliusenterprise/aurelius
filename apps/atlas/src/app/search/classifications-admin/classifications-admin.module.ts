import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { ReactiveFormsModule } from '@angular/forms';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { GovQualityApiClient } from '@models4insight/atlas/api';
import { TranslateModule } from '@ngx-translate/core';
import { ClassificationLabelModule } from '../components/classification-label';
import { ClassificationsAdminComponent } from './classifications-admin.component';

@NgModule({
    declarations: [ClassificationsAdminComponent],
    imports: [
        ClassificationLabelModule,
        CommonModule,
        FontAwesomeModule,
        ReactiveFormsModule,
        TranslateModule.forChild(),
    ],
    providers: [GovQualityApiClient],
})
export class ClassificationsAdminModule {}
