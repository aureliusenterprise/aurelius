import { Component, Inject, OnInit, Optional } from '@angular/core';
import { Route } from '@angular/router';
import {
  faArrowCircleDown,
  faBook,
  faUserShield,
  faEllipsisV,
  faSync,
} from '@fortawesome/free-solid-svg-icons';
import {
  AuthenticationService,
  Credentials,
  KeycloakService,
} from '@models4insight/authentication';
import { I18nService } from '@models4insight/i18n';
import { Feature } from '@models4insight/permissions';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { ShellAdminLink, ShellConfig, ShellConfigService, ShellRoleRequirement } from '../shell-config.service';
import { ShellService } from '../shell.service';

@Component({
  selector: 'models4insight-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss'],
})
export class HeaderComponent implements OnInit {
  readonly Feature = Feature;

  readonly appLogoPath: string;
  readonly appName: string;
  readonly standalone: boolean;
  readonly hideDocumentation: boolean;
  private readonly adminLinksFactory?: () => ShellAdminLink[];
  private readonly adminRole: string;

  readonly faArrowCircleDown = faArrowCircleDown;
  readonly faBook = faBook;
  readonly faUserShield = faUserShield;
  readonly faEllipsisV = faEllipsisV;
  readonly faSync = faSync;

  credentials$: Observable<Credentials>;
  isAdmin$: Observable<boolean>;
  adminLinks: ShellAdminLink[] = [];
  adminDialogOpen = false;
  currentLanguage$: Observable<string>;
  isAppInstallable$: Observable<boolean>;
  isUpdateAvailable$: Observable<boolean>;
  routes$: Observable<Route[]>;
  supportedLanguages$: Observable<string[]>;

  menuHidden = true;

  constructor(
    public i18nService: I18nService,
    private authenticationService: AuthenticationService,
    private shellService: ShellService,
    @Optional() private keycloakService: KeycloakService,
    @Optional() @Inject(ShellConfigService) config: ShellConfig = {}
  ) {
    this.appLogoPath = config.appLogoPath ?? 'assets/m4i-logo-notext.png';
    this.appName = config.appName;
    this.standalone = config.standalone ?? false;
    this.hideDocumentation = config.hideDocumentation ?? false;
    this.adminLinksFactory = config.adminLinks;
    this.adminRole = config.adminRole ?? 'ROLE_ADMIN';
  }

  ngOnInit() {
    this.credentials$ = this.authenticationService.credentials();
    // the Admin button: administrators only (realm role of the access token), and only where the app has links
    this.isAdmin$ = this.credentials$.pipe(
      map((credentials) => !!credentials && !!this.adminLinksFactory && this.hasAdminRole())
    );
    this.currentLanguage$ = this.i18nService.select('currentLanguage');
    this.isAppInstallable$ = this.shellService.select('isAppInstallable');
    this.isUpdateAvailable$ = this.shellService.select('isUpdateAvailable');
    this.routes$ = this.shellService.select('routes');
    this.supportedLanguages$ = this.i18nService.select('supportedLanguages');
  }

  applyUpdate() {
    this.shellService.applyUpdate();
  }

  triggerInstallPrompt() {
    this.shellService.installApp();
  }

  toggleMenu() {
    this.menuHidden = !this.menuHidden;
  }

  logout() {
    this.authenticationService.logout();
  }

  login() {
    this.authenticationService.login();
  }

  accountManagement() {
    this.authenticationService.accountManagement();
  }

  openAdminDialog() {
    this.adminLinks = (this.adminLinksFactory?.() ?? []).filter((link) => this.hasRoles(link.requires));
    this.adminDialogOpen = true;
  }

  closeAdminDialog() {
    this.adminDialogOpen = false;
  }

  /** Whether the user has at least one of the required roles (realm or client roles of the access token) */
  private hasRoles(requires?: ShellRoleRequirement): boolean {
    if (!requires) return true;
    const token = this.keycloakService?.tokenParsed;
    const realmRoles: string[] = token?.realm_access?.roles ?? [];
    if ((requires.realmRoles ?? []).some((role) => realmRoles.includes(role))) return true;
    return Object.entries(requires.clientRoles ?? {}).some(([clientId, roles]) => {
      const clientRoles: string[] = token?.resource_access?.[clientId]?.roles ?? [];
      return roles.some((role) => clientRoles.includes(role));
    });
  }

  private hasAdminRole(): boolean {
    const roles = this.keycloakService?.tokenParsed?.realm_access?.roles ?? [];
    return roles.includes(this.adminRole);
  }

  setLanguage(language: string) {
    this.i18nService.setLanguage(language);
  }
}
