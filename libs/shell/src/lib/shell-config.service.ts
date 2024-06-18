import { InjectionToken } from '@angular/core';

export interface ShellConfig {
  readonly appLogoPath?: string;
  readonly appName?: string;
  readonly appCopyright?: number;
  readonly standalone?: boolean;
  readonly hideDocumentation?: boolean;
}

export const ShellConfigService = new InjectionToken<ShellConfig>(
  'ShellConfig'
);
