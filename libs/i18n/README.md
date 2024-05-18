# I18N

The I18n module provides a common internationalization service.

## Initialization

You can configure this module with any number of languages. To initialize the I18n module, include the following in your `AppModule`:

```javascript
import { NgModule } from '@angular/core';
import { I18nModule } from '@models4insight/i18n';
import enUS from '../translations/en-US.json';
import frFR from '../translations/fr-FR.json';
import nlNL from '../translations/nl-NL.json';
import { AppComponent } from './app.component';

@NgModule({
  declarations: [AppComponent],
  imports: [
    I18nModule.forRoot({
      'en-US': enUS,
      'fr-FR': frFR,
      'nl-NL': nlNL
    })
  ],
  bootstrap: [AppComponent]
})
export class AppModule {}
```

The `I18nModule` is loaded as part of the Models4Insight `core`.

It is highly recommended that you use [IETF language tags](https://en.wikipedia.org/wiki/IETF_language_tag) as keys for the translation file mapping (as shown in the example).

Finally, to initialize the `I18nService` with the default language for your environment (in this case `en-US`), configure your `environment.ts` and `app.component.ts` as follows respectively:

```javascript
export const environment = {
  defaultLanguage: 'en-US'
};
```

```javascript
import { Component, OnInit } from '@angular/core';
import { I18nService } from '@models4insight/i18n';
import { environment } from '../environments/environment';

@Component({
  selector: 'models4insight-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  constructor(
    private i18nService: I18nService
  ) {}

  ngOnInit() {
    // Setup translations
    this.i18nService.init(environment.defaultLanguage);
  }
}
```

## Usage

Use the `TranslateService` from `@ngx-translate/core`, the `translate` directive, or the `| translate` pipe to inject translations into your app. Translations are updated whenever the user changes their chosen language. The original text is used as a key to look up the appropriate translation. If no translation is found, the original text is used.

### Translation File Example

Your translation files should be structured like the example below, where each file contains a dictionary with the same keys but with different translated values:

#### en-US.json

```json
{
  "hello world!": "hello world!"
}
```

#### fr-FR.json

```json
{
  "hello world!": "bonjour, le monde!"
}
```

### I18nService

The current language settings are controlled by the `I18nService`. You can set the current language to any of the values you used as keys for the configuration (so for example, `en-US` or `nl-NL`).

# Nx

This library was generated with [Nx](https://nx.dev).

## Running unit tests

Run `ng test i18n` to execute the unit tests.
