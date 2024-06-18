import { ModuleWithProviders, NgModule } from '@angular/core';
import {
  NotificationsConfig,
  NotificationsConfigService,
} from './notifications-config.service';

@NgModule()
export class NotificationsModule {
  static forRoot(
    config: NotificationsConfig = {}
  ): ModuleWithProviders<NotificationsModule> {
    return {
      ngModule: NotificationsModule,
      providers: [
        {
          provide: NotificationsConfigService,
          useValue: config,
        },
      ],
    };
  }
}
