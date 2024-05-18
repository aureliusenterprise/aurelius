import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';

import { Core } from '@models4insight/core';
import { environment } from '../environments/environment';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { AtlasComponent } from './components/cards/atlas/atlas.component';
import { AureliusComponent } from './components/cards/aurelius/aurelius.component';
import { CardsComponent } from './components/cards/cards.component';
import { FlinkComponent } from './components/cards/flink-box/flink.component';
import { KeyComponent } from './components/cards/key/key.component';
import { KibanaComponent } from './components/cards/kibana/kibana.component';
import { HeroComponent } from './components/hero/hero.component';
import { ServiceWorkerModule } from '@angular/service-worker';
import { KafkaComponent } from './components/cards/kafka-ui/kafka.component';

@NgModule({
  declarations: [
    AppComponent,
    CardsComponent,
    FlinkComponent,
    KibanaComponent,
    KeyComponent,
    AtlasComponent,
    AureliusComponent,
    HeroComponent,
    KafkaComponent,
  ],
  imports: [
    ...Core.imports(environment),
    BrowserModule,
    FontAwesomeModule,
    AppRoutingModule,
    ServiceWorkerModule.register('./ngsw-worker.js', {
      enabled: environment.production,
      // Register the ServiceWorker as soon as the application is stable
      // or after 30 seconds (whichever comes first).
      registrationStrategy: 'registerWhenStable:30000',
    }), // must be imported as the last module as it contains the fallback route
  ],
  providers: [],
  bootstrap: [AppComponent],
})
export class AppModule {}
