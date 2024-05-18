import { NgModule } from '@angular/core';
import { HeroModule } from '@models4insight/components';
import { HomeRoutingModule } from './home-routing.module';
import { HomeComponent } from './home.component';

@NgModule({
  imports: [HeroModule, HomeRoutingModule],
  declarations: [HomeComponent],
  providers: []
})
export class HomeModule {}
