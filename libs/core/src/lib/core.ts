import { NgModule } from '@angular/core';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { ServiceWorkerModule } from '@angular/service-worker';
import {
  AuthenticationConfig,
  AuthenticationModule,
} from '@models4insight/authentication';
import {
  GoogleAnalyticsConfig,
  GoogleAnalyticsModule,
} from '@models4insight/google-analytics';
import { HttpModule } from '@models4insight/http';
import { I18nConfig, I18nModule } from '@models4insight/i18n';
import { LoggerModule } from '@models4insight/logger';
import {
  NotificationsConfig,
  NotificationsModule,
} from '@models4insight/notifications';
import { ReduxModule } from '@models4insight/redux';
import { RepositoryModule } from '@models4insight/repository';
import { ServicesBranchModule } from '@models4insight/services/branch';
import { ClickstreamModule } from '@models4insight/services/clickstream';
import { ServicesModelModule } from '@models4insight/services/model';
import { ServicesProjectModule } from '@models4insight/services/project';
import { ServicesUserInfoModule } from '@models4insight/services/user-info';
import { ShellConfig, ShellModule } from '@models4insight/shell';
import { TaskManagerModule } from '@models4insight/task-manager';
import { VersionModule } from '@models4insight/version';

export interface CoreConfig {
  readonly googleAnalyticsMeasurementID: GoogleAnalyticsConfig['measurementID'];
  readonly i18n: I18nConfig;
  readonly keycloak: AuthenticationConfig;
  readonly notifications: NotificationsConfig;
  readonly production: boolean;
  readonly shell: ShellConfig;
  readonly telemetry: boolean;
}

/**
 * Represents the core of every Models4Insight application. Provides a method to generate an NgModule imports statement with a given configuration.
 */
export class Core {
  /**
   * Returns an NgModule imports statement for the core Models4Insight modules initialized with the given configuration parameters
   * @param config The configuration parameters with which to initialize the core modules
   */
  static imports(config: CoreConfig): NgModule['imports'] {
    return [
      BrowserAnimationsModule,
      LoggerModule.forRoot({ production: config.production }),
      HttpModule.forRoot({ production: config.production }),
      VersionModule.forRoot({
        appName: config.shell.appName,
        production: config.production,
      }),
      ReduxModule.forRoot({ production: config.production }),
      AuthenticationModule.forRoot(config.keycloak),
      GoogleAnalyticsModule.forRoot({
        measurementID: config.googleAnalyticsMeasurementID,
        production: config.production,
      }),
      I18nModule.forRoot(config.i18n),
      TaskManagerModule,
      ClickstreamModule.forRoot({
        app: config.shell.appName,
        enabled: config.telemetry,
      }),
      NotificationsModule.forRoot(config.notifications),
      RepositoryModule,
      ServicesBranchModule,
      ServicesModelModule,
      ServicesProjectModule.forRoot({ standalone: config.shell.standalone }),
      ServicesUserInfoModule,
      ServiceWorkerModule.register('./ngsw-worker.js', {
        enabled: config.production,
      }),
      ShellModule.forRoot(config.shell),
    ];
  }
}
