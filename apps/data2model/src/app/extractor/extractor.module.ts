import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { HeroModule } from '@models4insight/components';
import { HoldableModule } from '@models4insight/directives';
import { RepositoryModule } from '@models4insight/repository';
import { TranslateModule } from '@ngx-translate/core';
import { ApiModule } from '../api/api.module';
import { ExtractorRoutingModule } from './extractor-routing.module';
import { ExtractorComponent } from './extractor.component';
import { ExtractorService } from './extractor.service';
import { RuleEditorModule } from './rule-editor/rule-editor.module';

@NgModule({
  imports: [
    ApiModule,
    CommonModule,
    HeroModule,
    HoldableModule,
    TranslateModule,
    ExtractorRoutingModule,
    RepositoryModule,
    RuleEditorModule
  ],
  declarations: [ExtractorComponent],
  providers: [ExtractorService]
})
export class ExtractorModule {}
