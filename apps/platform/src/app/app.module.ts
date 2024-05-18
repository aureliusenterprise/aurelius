import { NgModule } from '@angular/core';
import { Core } from '@models4insight/core';
import { environment } from '../environments/environment';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { CoreModule } from './core/core.module';

@NgModule({
  declarations: [AppComponent],
  imports: [
    ...Core.imports(environment),
    CoreModule,
    AppRoutingModule // must be imported as the last module as it contains the fallback route
  ],
  bootstrap: [AppComponent]
})
export class AppModule {}
