import { Injector, NgModule } from '@angular/core';
import { AuthenticationService } from '@models4insight/authentication';
import { AUTH_TOKEN_PROVIDER, HttpModule } from '@models4insight/http';

@NgModule({
  imports: [HttpModule.forChild()],
  providers: [
    {
      provide: AUTH_TOKEN_PROVIDER,
      useExisting: AuthenticationService,
    },
  ],
})
export class RepositoryModule {
  static injector: Injector;

  constructor(injector: Injector) {
    RepositoryModule.injector = injector;
  }
}
