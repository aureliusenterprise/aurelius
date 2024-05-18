# Notifications

This module provides a common service for dispatching notifications to the user. These notifications integrate well with mobile operating systems, as well as Chrome on Windows. Other browser will have their own styles of notifications.

## Initialization
The notifications module relies on some configuration to set the default badge and icon that will be included in the notification.

To initialize the notifications module, please configure your `AppModule` as follows:

```javascript
import { NgModule } from '@angular/core';
import { NotificationsModule } from '@models4insight/notifications';
import { environment } from '../environments/environment';
import { AppComponent } from './app.component';

@NgModule({
  declarations: [AppComponent],
  imports: [
    NotificationsModule.forRoot({
      badgePath: 'assets/example-icon.png',
      iconPath: 'assets/example-icon.png'
    })
  ],
  bootstrap: [AppComponent]
})
export class AppModule {}
```

The `NotificationsModule` is loaded as part of the Models4Insight `core`.

## NotificationsService

Use the `NotificationsService` to dispatch notifications to the user. The `showNotification()` function allows for several options to customize the behavior of the notification, such as the message shown and sound played. It is also possible to group notifications, which is useful if they are related.

# Nx

This library was generated with [Nx](https://nx.dev).

## Running unit tests

Run `ng test notifications` to execute the unit tests.
