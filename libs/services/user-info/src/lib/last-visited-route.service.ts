import { Injectable } from '@angular/core';
import { getQueryParametersFromUrl } from '@models4insight/utils';
import { Dictionary } from 'lodash';
import { map } from 'rxjs/operators';
import { ServicesUserInfoModule } from './services-user-info.module';
import { UserInfoService } from './user-info.service';

/** Represents the last visited route in the application */
export interface LastVisitedRoute {
  /** The path of the last visited route */
  readonly path: string;
  /** Any query parameters applied to the last visited route */
  readonly queryParams?: Dictionary<string>;
}

@Injectable({
  providedIn: ServicesUserInfoModule,
})
export class LastVisitedRouteService {
  constructor(private readonly userInfoService: UserInfoService) {}

  /**
   * Returns a snapshot of the user's last visited route as a `Promise`
   */
  async getLastVisitedRoute() {
    const lastVisitedUrl = await this.userInfoService.get([
      'userInfo',
      'last_visited',
    ]);
    return this.handleFormatLastVisitedRoute(lastVisitedUrl);
  }

  /**
   * Returns an `Observable` stream of the user's last visited route
   */
  selectLastVisitedRoute() {
    return this.userInfoService
      .select(['userInfo', 'last_visited'])
      .pipe(
        map((lastVisitedUrl) =>
          this.handleFormatLastVisitedRoute(lastVisitedUrl)
        )
      );
  }

  /**
   * Sets the user's last vistited route to the given `url`
   * @param url The url of the user's last visited route
   */
  updateLastVisitedRoute(url: string) {
    const [pathAndParameters] = url.split('#');

    this.userInfoService.update({
      description: 'New last visited url available',
      path: ['userInfo', 'last_visited'],
      payload: pathAndParameters,
    });
  }

  private handleFormatLastVisitedRoute(
    lastVisitedUrl: string
  ): LastVisitedRoute {
    const [path] = lastVisitedUrl.split('?'),
      queryParams = getQueryParametersFromUrl(lastVisitedUrl);
    return { path, queryParams };
  }
}
