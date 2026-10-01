import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { KeycloakService } from '@models4insight/authentication';

/** Pages for administrators (realm role ROLE_ADMIN); others go back to the start page */
export const adminRoleGuard: CanActivateFn = () => {
    const roles = inject(KeycloakService).tokenParsed?.realm_access?.roles ?? [];
    return roles.includes('ROLE_ADMIN') || inject(Router).parseUrl('/search/browse');
};
