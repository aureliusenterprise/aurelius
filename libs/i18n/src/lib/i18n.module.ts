import {
  ModuleWithProviders,
  NgModule,
  Optional,
  SkipSelf,
} from '@angular/core';
import { TranslateModule } from '@ngx-translate/core';
import { I18nConfig, I18nConfigService } from './i18n-config.service';
import { I18nService } from './i18n.service';

@NgModule({
  imports: [TranslateModule.forRoot()],
  exports: [TranslateModule],
})
export class I18nModule {
  constructor(
    private readonly i18nService: I18nService,
    @Optional() @SkipSelf() parentModule: I18nModule
  ) {
    if (parentModule) {
      throw new Error(
        'I18nModule is already loaded. Import it in the AppModule only'
      );
    }
    this.i18nService.init();
  }

  static forRoot(config: I18nConfig): ModuleWithProviders<I18nModule> {
    return {
      ngModule: I18nModule,
      providers: [
        I18nService,
        {
          provide: I18nConfigService,
          useValue: config,
        },
      ],
    };
  }
}
