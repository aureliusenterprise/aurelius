import { ModuleWithProviders, NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';
import {
  AuthenticationConfig,
  AuthenticationConfigService,
} from './authentication-config.service';

@NgModule({
  imports: [RouterModule],
})
export class AuthenticationModule {
  static forRoot(
    config: AuthenticationConfig
  ): ModuleWithProviders<AuthenticationModule> {
    return {
      ngModule: AuthenticationModule,
      providers: [
        {
          provide: AuthenticationConfigService,
          useValue: config,
        },
      ],
    };
  }
}
