import { NgModule } from '@angular/core';
import { RepositoryModule } from '@models4insight/repository';
import { TrackLastVisitedRouteService } from './track-last-visited-route.service';

@NgModule({
  imports: [RepositoryModule],
  providers: [TrackLastVisitedRouteService]
})
export class CoreModule {
  constructor(trackLastVisitedRouteService: TrackLastVisitedRouteService) {
    trackLastVisitedRouteService.init();
  }
}
