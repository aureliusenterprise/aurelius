# Assets

This module provides common assets shared between apps, such as brand logos and icons.

## Usage

To include the shared assets in your application, include the following in the `angular.json` for your application project:

```json
{
  "$schema": "./node_modules/@angular/cli/lib/config/schema.json",
  "projects": {
    "<your-app-name>": {
      "architect": {
        "build": {
          "options": {
            "assets": [
              {
                "glob": "**/*",
                "input": "libs/assets/src/assets",
                "output": "/assets/"
              }
            ]
          }
        }
      }
    }
  }
}
```
