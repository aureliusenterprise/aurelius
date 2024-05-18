import { NgModule } from '@angular/core';
import { AtlasApiModule, ElasticApiModule } from '@models4insight/atlas/api';
import { Core } from '@models4insight/core';
import { I18nService } from '@models4insight/i18n';
import { environment } from '../environments/environment';
import enUS from '../translations/en-US.json';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';

@NgModule({
  declarations: [AppComponent],
  imports: [
    ...Core.imports(environment),
    AtlasApiModule,
    ElasticApiModule.forRoot(environment.atlas),
    AppRoutingModule, // must be imported as the last module as it contains the fallback route
  ],
  bootstrap: [AppComponent],
})
export class AppModule {
  constructor(private readonly i18nService: I18nService) {
    this.i18nService.setTranslation('en-US', enUS);
  }
}
