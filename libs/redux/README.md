# Redux

This module provides an extensible state management framework implementing [the Redux pattern](https://medium.com/@_bengarrison/an-introduction-to-redux-ea0d91de035e), as well as a common implementation which implements basic CRUD operations.

## Store

The base unit of our state management system is the `Store`. This is a service which keeps track of a dictionary of values. These values can be anything related to the feature which the service is responsible for. You can choose to create a single store for the entire application, or to create several stores managing different features. This will depend on the complexity of your application.

The `Store` does not allow its users to assign new values to the state directly. Instead, users must dispatch `Actions` to the `Store`, which will update the state in the order in which the actions were dispatched. This helps keep the behavior of the application predictable.

Likewise, the user cannot read values from the state directly. Instead, users must `select()` a particular part of the state they wish to observe. Alternatively, users can observe the overall `state` as well. The `state` property and the `select()` function return an [RxJS Observable](http://reactivex.io/rxjs/class/es6/Observable.js~Observable.html) of the selected state, which emits a new value every time that specific part of the state changes. This means that other parts of the application which depend on this state can be notified of any changes. This makes for a very effective trigger mechanism for various behaviors in the application.

### BasicStore

The `BasicStore` included with this module is a `Store` implementation which provides the following basic CRUD operations:

- `SET`
  - Destroy the current state and replace it state with the new state.
- `UPDATE`
  - Merge the new state with the old state, overriding any overlapping values.
- `DELETE`
  - Destroy the state at the given path, but otherwise keep the old state.

## Initialization

The `ReduxModule` can be passed configuration parameters to determine whether or not the `Store` should run in production mode. To initialize this module, please configure your `AppModule` as follows:

```javascript
import { NgModule } from '@angular/core';
import { ReduxModule } from '@models4insight/redux';
import { environment } from '../environments/environment';
import { AppComponent } from './app.component';

@NgModule({
  declarations: [AppComponent],
  imports: [
    ReduxModule.forRoot({ production: environment.production })
  ],
  bootstrap: [AppComponent]
})
export class AppModule {}
```

The `ReduxModule` is loaded as part of the Models4Insight `core`.

## Usage

For this example, we will be using the `BasicStore` implementation to manage a simple feature in our app.

First, let's define the state which our store will be managing as a TypeScript interface:

```javascript
export interface ExampleStoreContext {
    readonly counter?: number;
    readonly isLoading?: boolean;
}
```

The interface defines two properties for our Store, a counter and a loading indicator. Notice that both properties are `optional` and `readonly`. By defining the properties as `optional`, we allow for the state to be partially updated (leaving some parts stil blank). By defining the properties as `readonly`, we make sure our users know not to assign values to the state directly.

Next, let's define a service to manage our state. The service should extend `BasicStore` and give `ExampleStoreContext` as its type parameter:

```javascript
import { Injectable } from '@angular/core';
import { BasicStore } from '@models4insight/redux';

@Injectable()
export class ExampleService extends BasicStore<ExampleStoreContext> {}
```

You now have a store which manages the example state, which is injectable into any component or service. Next, let's define some triggers based on our state values. It is recommended to include these triggers as part of an `init()` method called in the constructor of the service.

```javascript
constructor() {
    this.init();
}

private init() {

    // Set the initial state
    this.set({
        description: 'Set initial state',
        payload: {
            counter: 0,
            isLoading: false
        }
    });

    // Whenever the counter updates, print the new value to the console.
    this.select('counter').subscribe(value => console.log(value));

    // Update the value of the counter
    this.update({
        description: 'Set counter to 1',
        payload: {
            counter: 1
        }
    });

    // Update the value of isLoading
    this.update({
        description: 'Set isLoading to true',
        payload: {
            isLoading: true
        }
    });

    // Delete the counter value
    this.delete({
        description: 'Remove the counter',
        path: ['counter']
    });
}
```

The init function first sets a default value for both our properties. Here we set counter to 0. Next, we define a trigger on counter, which prints the counted value every time it changes. Next, we update the value of the counter and set it to 1. Note that two values will get printed. Once for the initial value which is present at the time of subscription, and once for the updated value which comes in after we have subscribed to it. When we update the value of isLoading, the counter will not be printed because its value did not change. Likewise, when we delete the counter, it will not emit because the value does not exist anymore.

### StoreService

Additionally, this module provides an overall StoreService which to which individual stores can register. This allows for the creation of a snapshot of all registered stores. This can be especially handy for error reporting and debugging. To register a store with the StoreService, you can include the following:

```javascript
import { Injectable } from '@angular/core';
import { BasicStore, StoreService } from '@models4insight/redux';

@Injectable()
export class ExampleService extends BasicStore<ExampleStoreContext>() {

    constructor(storeService: StoreService) {
        super({name: 'ExampleService', storeService);
        this.init();
    }

    private init() { }
}
```

## Redux DevTools Extension

In development mode, `Store` emits all state changes to [Redux DevTools](https://github.com/zalmoxisus/redux-devtools-extension). This browser plugin shows a detailed history of all state updates while it is active. Great for debugging. It is available for Chrome and Firefox.

# Nx

This library was generated with [Nx](https://nx.dev).

## Running unit tests

Run `ng test redux` to execute the unit tests.
