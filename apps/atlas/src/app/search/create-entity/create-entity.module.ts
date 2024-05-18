import { NgModule } from '@angular/core';
import { EditorModule } from '../components/editor/editor.module';
import { EntityDetailsService } from '../services/entity-details/entity-details.service';
import { CreateEntityComponent } from "./create-entity.component";

@NgModule({
  declarations: [CreateEntityComponent],
  imports: [
    EditorModule,
  ],
  exports: [CreateEntityComponent],
  providers: [EntityDetailsService]
})
export class CreateEntityModule {}
