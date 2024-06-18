import { CommonModule } from '@angular/common';
import { ModuleWithProviders, NgModule } from '@angular/core';
import { RouteReuseStrategy, RouterModule } from '@angular/router';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { I18nService } from '@models4insight/i18n';
import { FeatureModule } from '@models4insight/permissions';
import { TranslateModule } from '@ngx-translate/core';
import enUS from '../translations/en-US.json';
import { FooterComponent } from './footer/footer.component';
import { HeaderComponent } from './header/header.component';
import { LoadingComponent } from './loading/loading.component';
import { PipelineTaskComponent } from './pipeline/pipeline-task/pipeline-task.component';
import { PipelineComponent } from './pipeline/pipeline.component';
import { RouteReusableStrategy } from './route-reusable-strategy';
import { ShellConfig, ShellConfigService } from './shell-config.service';
import { ShellComponent } from './shell.component';

@NgModule({
  imports: [
    CommonModule,
    FeatureModule,
    FontAwesomeModule,
    RouterModule,
    TranslateModule.forChild(),
  ],
  declarations: [
    HeaderComponent,
    FooterComponent,
    ShellComponent,
    LoadingComponent,
    PipelineComponent,
    PipelineTaskComponent,
  ],
})
export class ShellModule {
  constructor(private i18nService: I18nService) {
    this.i18nService.setTranslation('en-US', enUS);
  }

  static forRoot(config: ShellConfig = {}): ModuleWithProviders<ShellModule> {
    return {
      ngModule: ShellModule,
      providers: [
        {
          provide: ShellConfigService,
          useValue: config,
        },
        {
          provide: RouteReuseStrategy,
          useClass: RouteReusableStrategy,
        },
      ],
    };
  }
}
