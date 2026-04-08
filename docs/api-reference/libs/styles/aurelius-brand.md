# aurelius-brand

[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=aurelius-brand&metric=sqale_rating&token=7a547436f2892554c971e2f91b0a92f98187065f)](https://sonarcloud.io/summary/new_code?id=aurelius-brand)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=aurelius-brand&metric=reliability_rating&token=7a547436f2892554c971e2f91b0a92f98187065f)](https://sonarcloud.io/summary/new_code?id=aurelius-brand)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=aurelius-brand&metric=security_rating&token=7a547436f2892554c971e2f91b0a92f98187065f)](https://sonarcloud.io/summary/new_code?id=aurelius-brand)

This library provides the Aurelius brand styles and assets for use in Aurelius projects.

## Installation

You can include `aurelius-brand` styles in your project by adding them to your root `styles.scss` file:

```scss
@use "@aurelius/brand/src/main";
```

Then, you can include the `aurelius-brand` assets in your project by adding the following to your `angular.json`:

```json
{
    "assets": [
        {
            "source": "libs/styles/aurelius-brand/assets",
            "target": "assets/aurelius-brand"
        }
    ]
}
```

Ensure the path points to the correct location of the `aurelius-brand` library.
