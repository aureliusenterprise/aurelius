# Permissions

This library provides functions for permissions management. It consists of the following modules:

## FeatureModule

The feature module provides funcitons and components to help (un)lock parts of the application based on the subscription level of the user.
Features are defined by name, and by convention are namespaced using a `.` notation (for example `application.module.feature`).
The feature name is used to check the subscription level with the back-end, so any feature name needs to be match what is defined there.

### FeatureDirective

Use the `models4insight-feature` directive to remove sections of a page the user should not be able to see based on their subscription level.
Adding a feature constraint works similar to adding a `*ngIf` condition to an element.
However, instead of adding a condition that evaluates to true or false, you pass the feature name as an argument.
The `models4insight-feature` directive should always be used with an `*` notation.

#### Example

```html
<button
  id="retrieveButton"
  *models4insight-feature="'models4insight.platform.retrieve'"
></button>
```

In the example above, if the user does not have a sufficient subscription level for the `models4insight.platform.retrieve` feature, the `retrieveButton` element will not appear on the page.

## ProjectPermissionModule

The `ProjectPermissionModule` provides functions and components to help (un)lock parts of the application based on the user's permission level in a particular project.

The following project permission levels are available:

| Role name       | Description                                                |
| --------------- | ---------------------------------------------------------- |
| `OWNER`         | Can perform delete actions and assign other owners         |
| `MAINTAINER`    | Can alter properties and settings including access control |
| `CONTRIBUTOR`   | Can commit changes to the model                            |
| `MODEL_USER`    | Can retrieve models in Archi format                        |
| `BUSINESS_USER` | Can use the model explorer and business dashboards         |

Project permission levels can be referenced via the `ProjectPermissionLevel` enum.

### ProjectPermissionDirective

Use the `models4insight-project-permission` directive to remove sections of a page the user should not be able to see based on their project permission level.
Adding a project permission constraint works similar to adding a `*ngIf` condition to an element.
However, instead of adding a condition that evaluates to true or false, you pass the project or the project ID, along with the minimum permission level.
The `models4insight-project-permission` directive should always be used with an `*` notation.

#### Example

```html
<button
  id="retrieveButton"
  *models4insight-project-permission="
    project;
    level: PermissionLevel.MODEL_USER
  "
></button>
```

In the example above, the `retrieveButton` element will appear on the page only if the user has a permission level of `MODEL_USER` or above for the given project.

### HasProjectPermissionDirective

Use the `models4insight-has-project-permission` directive to expose a variable which indicates whether the user has the required project permission level.
This is useful when you need to customize the behavior of an element based on the permission level of the user, rather than simply removing the element.
Like for the `models4insight-project-permission` directive, you pass the project or the project ID, along with the minimum permission level.
In addition, you can assign a template variable which reflects the permission state as either `true` or `false`.
The `models4insight-has-project-permission` directive should always be used with an `*` notation.

#### Example

```html
<button
  id="retrieveButton"
  *models4insight-has-project-permission="
    project;
    level: PermissionLevel.MODEL_USER;
    let isModelUser = hasPermission
  "
  [class.is-static]="!isModelUser"
></button>
```

In the example above, the `retrieveButton` element will be assigned the `is-static` class if the user does not have a permission level of `MODEL_USER` or above for the given project.

### ProjectPermissionService

The `ProjectPermissionService` exposes the `checkPermissions()` function, which returns an observable stream of whether or not the current user has a sufficient permission level for a given project. Use this function whenever you need to evaluate user permissions as part of your code rather than as part of a page. The above directives also use this service under the hood.

## BranchPermissionModule

The `BranchPermissionModule` provides functions and components to help (un)lock parts of the application based on the user's permission level in a particular branch of a particular project.

The following branch permission levels are available:

| Role name       | Description                                                |
| --------------- | ---------------------------------------------------------- |
| `OWNER`         | Can perform delete actions and assign other owners         |
| `MAINTAINER`    | Can alter properties and settings including access control |
| `CONTRIBUTOR`   | Can commit changes to the model                            |
| `MODEL_USER`    | Can retrieve models in Archi format                        |
| `BUSINESS_USER` | Can use the model explorer and business dashboards         |

Branch permission levels can be referenced via the `BranchPermissionLevel` enum.

### BranchPermissionDirective

Use the `models4insight-branch-permission` directive to remove sections of a page the user should not be able to see based on their branch permission level.
Adding a branch permission constraint works similar to adding a `*ngIf` condition to an element.
However, instead of adding a condition that evaluates to true or false, you pass the project or project ID, along with the branch name and minimum permission level.
The `models4insight-project-permission` directive should always be used with an `*` notation.

#### Example

```html
<button
  id="retrieveButton"
  *models4insight-branch-permission="
    project;
    branch: branchName;
    level: PermissionLevel.MODEL_USER
  "
></button>
```

In the example above, the `retrieveButton` element will appear on the page only if the user has a permission level of `MODEL_USER` or above for the given branch of the given project.

### HasBranchPermissionDirective

Use the `models4insight-has-branch-permission` directive to expose a variable which indicates whether the user has the required branch permission level for the given project.
This is useful when you need to customize the behavior of an element based on the permission level of the user, rather than simply removing the element.
Like for the `models4insight-branch-permission` directive, you pass the project or the project ID, along with the branch name and minimum permission level.
In addition, you can assign a template variable which reflects the permission state as either `true` or `false`.
The `models4insight-has-branch-permission` directive should always be used with an `*` notation.

#### Example

```html
<button
  id="retrieveButton"
  *models4insight-has-branch-permission="
    project;
    branch: branchName;
    level: PermissionLevel.MODEL_USER;
    let isModelUser = hasPermission
  "
  [class.is-static]="!isModelUser"
></button>
```

In the example above, the `retrieveButton` element will be assigned the `is-static` class if the user does not have a permission level of `MODEL_USER` or above for the given branch of the given project.

### BranchPermissionService

The `BranchPermissionService` exposes the `checkPermissions()` function, which returns an observable stream of whether or not the current user has a sufficient permission level for a given branch of a given project. Use this function whenever you need to evaluate user permissions as part of your code rather than as part of a page. The above directives also use this service under the hood.

# Nx

This library was generated with [Nx](https://nx.dev).

## Running unit tests

Run `ng test permissions` to execute the unit tests.
