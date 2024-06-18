import { Injectable } from '@angular/core';
import { AuthenticationService } from '@models4insight/authentication';
import { BasicStore, MonitorAsync, StoreService } from '@models4insight/redux';
import {
  getUserInfo,
  updateUserInfo,
  UserInfo,
} from '@models4insight/repository';
import { ManagedTask } from '@models4insight/task-manager';
import { untilDestroyed } from '@models4insight/utils';
import { identity } from 'lodash';
import { partition } from 'rxjs';
import { filter, pairwise, switchMap, debounceTime } from 'rxjs/operators';
import { ServicesUserInfoModule } from './services-user-info.module';

export interface UserInfoStoreContext {
  readonly isAddingFavoriteProject?: boolean;
  readonly isRemovingFavoriteProject?: boolean;
  readonly isRetrievingUserInfo?: boolean;
  readonly isUpdatingUserInfo?: boolean;
  readonly userInfo?: UserInfo;
}

const defaultUserInfoServiceState: UserInfoStoreContext = {
  isAddingFavoriteProject: false,
  isRemovingFavoriteProject: false,
  isRetrievingUserInfo: false,
  isUpdatingUserInfo: false,
};

@Injectable({
  providedIn: ServicesUserInfoModule,
})
export class UserInfoService extends BasicStore<UserInfoStoreContext> {
  constructor(
    private readonly authenticationService: AuthenticationService,
    readonly storeService: StoreService
  ) {
    super({
      defaultState: defaultUserInfoServiceState,
      name: 'UserInfoService',
      storeService,
    });
    this.init();
  }

  /**
   * Returns the current user preferences.
   */
  get userinfo() {
    return this.select('userInfo');
  }

  private init() {
    const [authenticated, notAuthenticated] = partition(
      this.authenticationService.isAuthenticated(),
      identity
    );

    // Whenever a user authenticates, retrieve their userinfo
    authenticated
      .pipe(
        switchMap(() => this.handleRetrieveUserInfo()),
        untilDestroyed(this)
      )
      .subscribe();

    // Whenever the user is not or no longer authenticated, reset the userinfo
    notAuthenticated.pipe(untilDestroyed(this)).subscribe(() => this.reset());

    // Whenever the user info updates, send it over to the back end.
    // Don't update on the initial load, or when another user logs in.
    this.select('userInfo')
      .pipe(
        pairwise(),
        filter(
          ([old, current]) =>
            old?.userid && current?.userid && old?.userid === current?.userid
        ),
        debounceTime(50),
        switchMap(([, userInfo]) => this.handleUpdateUserInfo(userInfo)),
        untilDestroyed(this)
      )
      .subscribe();
  }

  @ManagedTask('Retrieving your preferences', { isQuiet: true })
  @MonitorAsync('isRetrievingUserInfo')
  private async handleRetrieveUserInfo() {
    const userInfo = await getUserInfo().toPromise();

    this.update({
      description: 'New user info available',
      payload: { userInfo },
    });

    return userInfo;
  }

  @ManagedTask('Saving your preferences', { isQuiet: true })
  @MonitorAsync('isUpdatingUserInfo')
  private async handleUpdateUserInfo(userInfo: UserInfo) {
    return updateUserInfo(userInfo).toPromise();
  }
}
