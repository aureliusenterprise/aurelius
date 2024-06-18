import { InjectionToken } from '@angular/core';
import { Dictionary } from 'lodash';

export interface LanguagesConfig {
  [IETF_LANGUAGE_TAg: string]: Dictionary<string>;
}

/**
 * Configure the available languages by adding dictionaries containing translations, keyed by IETF language tag.
 */
export interface I18nConfig {
  defaultLanguage: string;
  languages: LanguagesConfig;
}

export const I18nConfigService = new InjectionToken<I18nConfig>('I18nConfig');
