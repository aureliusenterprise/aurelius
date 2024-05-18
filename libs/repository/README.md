# Repository

The `RepositoryModule` provides functions for interacting with the Models4Insight Repository REST API. It implements interfaces for all data objects exchanged, as well as adapters for all the different REST API functions. It also provides several utility functions based around API calls, such as downloading a model or monitoring the status of an asynchronous API function.

## Usage

The `RepositoryModule` is part of the Models4Insight `core`, and is initialized as part of the `AppModule`. If an API function is used without initializing the `RepositoryModule`, an error is thrown. This means that modules loaded before the `RepositoryModule` cannot use API functions.

After initializing the `RepositoryModule`, any API function can be imported and used directly in your components and services. All API functions return an `Observable` stream of the API response.

### Example

Below is an example of a module importing the `RepositoryModule`:

```javascript
import { NgModule } from '@angular/core';
import { RepositoryModule } from '@models4insight/repository';

@NgModule({
  imports: [RepositoryModule]
})
export class ExampleModule {}
```

Next is an example of a service using an API function:

```javascript
import { Injectable } from '@angular/core';
import { exampleApiFunction } from '@models4insight/repository';
import { ExampleModule } from './example.module';

@Injectable({
  providedIn: ExampleModule
})
export class ExampleService {

    constructor() {
        this.init();
    }

    private async init() {
        const apiResponse = await exampleApiFunction().toPromise();
    }
}
```

## Dependencies

This module depends on the `HttpClient` provided by `@models4insight/http`.

# Nx

This library was generated with [Nx](https://nx.dev).

## Running unit tests

Run `ng test repository` to execute the unit tests.
