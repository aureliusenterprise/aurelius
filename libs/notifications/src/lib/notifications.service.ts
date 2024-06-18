import { Inject, Injectable, Optional } from '@angular/core';
import { now } from 'lodash';
import { v4 as uuid } from 'uuid';
import {
  NotificationsConfig,
  NotificationsConfigService,
} from './notifications-config.service';
import { NotificationsModule } from './notifications.module';

export interface NotificationOptions {
  /** Detailed message */
  body?: string;
  /** Whether or not to play a notification sound */
  silent?: boolean;
  /** Optional notification ID. Use this to group notifications. If not set, a random UUID is used. */
  tag?: string;
}

@Injectable({
  providedIn: NotificationsModule,
})
export class NotificationsService {
  private serviceWorkerRegistration: ServiceWorkerRegistration;

  constructor(
    @Optional()
    @Inject(NotificationsConfigService)
    private config: NotificationsConfig = {}
  ) {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.ready.then((registration) => {
        this.serviceWorkerRegistration = registration;
      });
    }
  }

  /**
   * Attempts to show a notification to the user.
   * Notifications are user opt-in based.
   * The user will be prompted to grant permission if not already granted or denied.
   * Prefers the service worker persistent notification interface, but falls back to browser notifications if the service worker is unavailable.
   * Returns the tag of the notification.
   */
  async showNotification(
    /** The notification message that will be shown to the user */
    title: string,
    /** Additional options */
    options: NotificationOptions = {}
  ): Promise<string | null> {
    let result = null;
    if ('Notification' in window) {
      const permission = await Notification.requestPermission();
      if (permission === 'granted') {
        const config = Object.assign(
          {
            badge: this.config.badgePath,
            icon: this.config.iconPath,
            tag: (result = uuid()),
            timestamp: now(),
          },
          options
        );
        result = config.tag;
        if (this.serviceWorkerRegistration) {
          this.serviceWorkerRegistration.showNotification(title, config);
        } else {
          new Notification(title, config);
        }
      }
    }
    return result;
  }
}
