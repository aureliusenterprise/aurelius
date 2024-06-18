import { Inject, Injectable } from '@angular/core';
import { Title } from '@angular/platform-browser';
import {
  ActivatedRouteSnapshot,
  Router,
  RoutesRecognized,
} from '@angular/router';
import { Logger } from '@models4insight/logger';
import { BasicStore, StoreService } from '@models4insight/redux';
import { TranslateService } from '@ngx-translate/core';
import { includes } from 'lodash';
import { combineLatest, merge } from 'rxjs';
import {
  distinctUntilChanged,
  filter,
  map,
  pluck,
  shareReplay,
  switchMapTo,
} from 'rxjs/operators';
import { I18nConfig, I18nConfigService } from './i18n-config.service';

const log = new Logger('I18nService');
const languageKey = 'language';

/**
 * Pass-through function to mark a string for translation extraction.
 * @param s The string to extract for translation.
 * @return The same string.
 */
export function extract(s: string) {
  return s;
}

export interface I18nStoreContext {
  defaultLanguage?: string;
  supportedLanguages?: string[];
  userLanguage?: string;
  currentLanguage?: string;
}

/**
 * Passes through all child nodes of the given `ActivatedRouteSnapshot` and returns the furthest page title found.
 * If no title is found, returns `undefined`.
 */
function findTitle(activatedRoute: ActivatedRouteSnapshot): string {
  let title: string;
  if (activatedRoute.firstChild) {
    title = findTitle(activatedRoute.firstChild);
  }
  if (!title) {
    title = activatedRoute.data['title'];
  }
  return title;
}

@Injectable()
export class I18nService extends BasicStore<I18nStoreContext> {
  defaultLanguage: string;

  constructor(
    private readonly router: Router,
    private readonly titleService: Title,
    private readonly translateService: TranslateService,
    @Inject(I18nConfigService) config: I18nConfig,
    storeService: StoreService
  ) {
    super({
      defaultState: {
        defaultLanguage: config.defaultLanguage,
        supportedLanguages: Object.keys(config.languages),
        userLanguage:
          localStorage.getItem(languageKey) ||
          translateService.getBrowserCultureLang(),
      },
      name: 'I18nService',
      storeService,
    });
    Object.entries(config.languages).forEach(([lang, translations]) =>
      this.setTranslation(lang, translations)
    );
  }

  /**
   * Initializes i18n for the application.
   * Loads language from local storage if present, or sets default language.
   * @param defaultLanguage The default language to use.
   * @param supportedLanguages The list of supported languages.
   */
  init() {
    // Whenever the current language changes, update the store
    this.translateService.onLangChange
      .pipe(pluck('lang'))
      .subscribe((lang: string) =>
        this.update({
          payload: { currentLanguage: lang },
          description: 'Current language settings updated',
        })
      );

    // Whenever new route data becomes available, look up the current page title
    const pageTitle = this.router.events.pipe(
      filter((data) => data instanceof RoutesRecognized),
      map((data: RoutesRecognized) => findTitle(data.state.root)),
      distinctUntilChanged(),
      shareReplay()
    );

    // Whenever the current language or the page title changes, update the page title
    merge([this.translateService.onLangChange, pageTitle])
      .pipe(switchMapTo(pageTitle))
      .subscribe((title) => {
        if (title) {
          this.titleService.setTitle(this.translateService.instant(title));
        }
      });

    // Whenever the current language changes, cache it as the the user's preferred language in the localStorage
    this.select('currentLanguage').subscribe((lang) =>
      localStorage.setItem(languageKey, lang)
    );

    // Whenever the user's language, supported languages, or default language update, update the `TranslateService` to use this language.
    combineLatest([
      this.select('userLanguage'),
      this.select('supportedLanguages'),
      this.select('defaultLanguage'),
    ])
      .pipe(
        map(([userLang, supportedLangs, defaultLang]) => {
          let lang = userLang;
          let isSupportedLanguage = includes(supportedLangs, lang);
          // If no exact match is found, search without the region
          if (userLang && !isSupportedLanguage) {
            const noRegion = lang.split('-')[0];
            lang =
              supportedLangs.find((supportedLanguage) =>
                supportedLanguage.startsWith(noRegion)
              ) || '';
            isSupportedLanguage = Boolean(lang);
          }
          // Fallback if language is not supported
          if (!isSupportedLanguage) {
            lang = defaultLang;
          }
          return lang;
        })
      )
      .subscribe((lang) => {
        log.debug(`Language set to ${lang}`);
        this.translateService.use(lang);
      });
  }

  /**
   * Sets the current language.
   * Note: The current language is saved to the local storage.
   * If no parameter is specified, the language is loaded from local storage (if present).
   * @param language The IETF language code to set.
   */
  setLanguage(language: string) {
    this.update({
      payload: { userLanguage: language },
      description: 'New preferred language selected',
    });
  }

  /** Merges a set of translations with the current dictionary for the given language. */
  setTranslation(
    /** The IETF language code associated with the translations */
    language: string,
    /** The translations to merge with the current dictionary */
    translations: Object
  ) {
    this.translateService.setTranslation(language, translations, true);
  }
}
