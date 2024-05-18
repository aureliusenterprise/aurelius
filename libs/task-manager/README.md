# Task Manager

This module provides `TaskManagerService`, which helps keep track of currently running asynchronous `Task`s. Once a `Task` is registered, it can have any one of four states:

- Pending
- Active
- Completed
- Error

A `Task` consists of one or more [RxJS Observables](http://reactivex.io/rxjs/class/es6/Observable.js~Observable.html). You can set up a `Task` by adding any number of `Observable`s to it, which will be executed in sequence. These `Observable`s can also depend on eachother for input.

You can run a `Task` by subscribing to its `executable` property. The `executable` keeps track of which step it is currently processing and notifies the `TaskManagerService` of its progress, and implements error handling.

## Usage

To create a task, you can either use the `createTask()` function of the `TaskManagerService`, or use the `@ManagedTask()` decorator. The managed task decorator is recommended if you need to create a `Task` that consists of a single step. You can pass a description of the `Task` along with the decorator. If you need to create a more complex task, consisting of multiple operations, it is recommended to call `createTask()` to obtain a `Task` instance, and add steps individually. See the example below:

```javascript
import { ManagedTask, TaskManagerService } from '@models4insight/task-manager';
import { of } from 'rxjs';
import { mapTo } from 'rxjs/operators';

@ManagedTask('Doing something simple')
function simpleTask() {
  return of('example');
}

function complexTask() {
  const step1 = of('step1'),
    step2 = step1.pipe(mapTo('step2')),
    task = this.taskManagerService.createTask([{
      description: 'Doing something',
      operation: step1
    }, {
      description: 'Doing something else',
      operation: step2
    }]);
  return task.executable;
}
```

# Nx

This library was generated with [Nx](https://nx.dev).

## Running unit tests

Run `ng test task-manager` to execute the unit tests.
