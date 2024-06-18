/// <reference types="gtag.js" />

import { Inject, Injectable } from '@angular/core';
import { NavigationEnd, Router } from '@angular/router';
import { distinctUntilChanged, filter, map } from 'rxjs/operators';
import {
  GoogleAnalyticsConfig,
  GoogleAnalyticsConfigService,
} from './google-analytics-config.service';

declare const gtag: Gtag.Gtag;

@Injectable()
export class GoogleAnalyticsService {
  constructor(
    private router: Router,
    @Inject(GoogleAnalyticsConfigService)
    private config: GoogleAnalyticsConfig = {}
  ) {}

  init() {
    // Listen for navigation end events on the router.
    // Whenever the url changes, record a new pageview
    this.router.events
      .pipe(
        filter((event) => event instanceof NavigationEnd),
        map((event: NavigationEnd) => event.urlAfterRedirects),
        distinctUntilChanged()
      )
      .subscribe((url) => {
        if (gtag) {
          gtag('config', this.config.measurementID, {
            page_path: url,
          });
        } else {
          throw new Error(
            'Tried submitting Google analytics measurement data, but Google analytics functions were not loaded properly.'
          );
        }
      });
  }
}
