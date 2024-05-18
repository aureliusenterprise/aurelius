# Logger

This module provides a common logger which prints messages to the console. The logger provides the following log levels:

- `DEBUG`
- `INFO`
- `WARNING`
- `ERROR`

## Initialization

By default, the logger runs in development mode. In development mode, the logger prints messages from all log levels.

Alternatively, you can run the logger in production mode to only include `WARNING` and `ERROR` messages. To enable production mode, please include the following in your `app.module.ts`:

```javascript
import { NgModule } from '@angular/core';
import { LoggerModule } from '@models4insight/logger';
import { environment } from './environments/environment';

@NgModule({
  imports: [LoggerModule.forRoot({ production: environment.production })]
})
export class AppModule {}
```

The `LoggerModule` is loaded as part of the Models4Insight `core`.

## Usage

To use the logger, create a new instance of the logger with the name of your component or service as follows:

```javascript
import { Injectable } from '@angular/core';
import { Logger } from '@models4insight/logger';

const log = new Logger('ExampleService');

@Injectable()
export class ExampleService {
  constructor() {
    try {
      log.debug('debug');
      log.info('info');
      log.warning('warning');
      throw new Error('error');
    } catch (error) {
      log.error(error);
    }
  }
}
```

# Nx

This library was generated with [Nx](https://nx.dev).

## Running unit tests

Run `ng test logger` to execute the unit tests.
