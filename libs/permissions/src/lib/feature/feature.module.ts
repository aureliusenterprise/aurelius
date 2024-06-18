import { NgModule } from '@angular/core';
import { RepositoryModule } from '@models4insight/repository';
import { FeatureDirective } from './feature.directive';
import { FeatureService } from './feature.service';

@NgModule({
  imports: [RepositoryModule],
  declarations: [FeatureDirective],
  providers: [FeatureService],
  exports: [FeatureDirective],
})
export class FeatureModule {}
