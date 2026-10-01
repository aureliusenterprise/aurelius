import { InjectionToken } from '@angular/core';

/** A link of the header's Admin dialog (titles and descriptions are translation keys) */
export interface ShellAdminLink {
  readonly url: string;
  readonly title: string;
  readonly description: string;
}

export interface ShellConfig {
  readonly appLogoPath?: string;
  readonly appName?: string;
  readonly appCopyright?: number;
  readonly standalone?: boolean;
  readonly hideDocumentation?: boolean;
  /**
   * Links of the Admin button in the header (between Documentation and the language selection), computed when the
   * dialog opens. Without it there is no Admin button.
   */
  readonly adminLinks?: () => ShellAdminLink[];
  /** Keycloak realm role that sees the Admin button (default ROLE_ADMIN) */
  readonly adminRole?: string;
}

export const ShellConfigService = new InjectionToken<ShellConfig>(
  'ShellConfig'
);
