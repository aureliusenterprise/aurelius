import { InjectionToken } from '@angular/core';

export interface NotificationsConfig {
  readonly badgePath?: string;
  readonly iconPath?: string;
}

export const NotificationsConfigService =
  new InjectionToken<NotificationsConfig>('NotificationsConfig');
