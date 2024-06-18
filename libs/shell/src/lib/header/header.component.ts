import { Component, Inject, OnInit, Optional } from '@angular/core';
import { Route } from '@angular/router';
import {
  faArrowCircleDown,
  faBook,
  faEllipsisV,
  faSync,
} from '@fortawesome/free-solid-svg-icons';
import {
  AuthenticationService,
  Credentials,
} from '@models4insight/authentication';
import { I18nService } from '@models4insight/i18n';
import { Feature } from '@models4insight/permissions';
import { Observable } from 'rxjs';
import { ShellConfig, ShellConfigService } from '../shell-config.service';
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

  readonly faArrowCircleDown = faArrowCircleDown;
  readonly faBook = faBook;
  readonly faEllipsisV = faEllipsisV;
  readonly faSync = faSync;

  credentials$: Observable<Credentials>;
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
    @Optional() @Inject(ShellConfigService) config: ShellConfig = {}
  ) {
    this.appLogoPath = config.appLogoPath ?? 'assets/m4i-logo-notext.png';
    this.appName = config.appName;
    this.standalone = config.standalone ?? false;
    this.hideDocumentation = config.hideDocumentation ?? false;
  }

  ngOnInit() {
    this.credentials$ = this.authenticationService.credentials();
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

  setLanguage(language: string) {
    this.i18nService.setLanguage(language);
  }
}
