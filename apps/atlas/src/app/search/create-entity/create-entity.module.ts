import { NgModule } from '@angular/core';
import { EditorModule } from '../components/editor/editor.module';
import { EntityDetailsService } from '../services/entity-details/entity-details.service';
import { CreateEntityComponent } from './create-entity.component';
import { TranslateModule } from '@ngx-translate/core';

@NgModule({
    declarations: [CreateEntityComponent],
    imports: [EditorModule, TranslateModule],
    exports: [CreateEntityComponent],
    providers: [EntityDetailsService],
})
export class CreateEntityModule {}
