import { NgModule } from '@angular/core';
import { EditorModule } from '../components/editor/editor.module';
import { EntityDetailsService } from '../services/entity-details/entity-details.service';
import { EditEntityResolver } from './edit-entity-resolver';
import { EditEntityRoutingModule } from './edit-entity-routing.module';
import { EditEntityComponent } from './edit-entity.component';
import { TranslateModule } from '@ngx-translate/core';

@NgModule({
    declarations: [EditEntityComponent],
    imports: [EditorModule, EditEntityRoutingModule, TranslateModule],
    providers: [EditEntityResolver, EntityDetailsService],
})
export class EditEntityModule {}
