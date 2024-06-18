# FuzzySearchInput

This module provides the `models4insight-fuzzy-search-input` component, which exists of a text input.
This text input triggers the calculation of suggestions whenever the user changes their search query.
The suggestions are derived from a set of predefined search terms.
The component uses a combination of contains search and `SymSpell` fuzzy search to arrive at the suggestions.
Search suggestions are useful whenever you want to autofill a field based on some partial input, or when you expect that the user does not know how the thing they are searching for is spelled (e.g. a username or email address).

## Usage

The `models4insight-fuzzy-search-input` component defines the following inputs:

- `filterTerms`: An array of search terms which should always be excluded from the suggestions
- `query`: Use this input if you want to set the current search query string externally, e.g. to provide a default value
- `terms`: An array of search terms used to define the possible suggestions

Further, the component defines the following outputs:

- `isUpdatingSuggestions`: Emits a boolean value which indicates whether or not the search is currently running
- `queryChanged`: Emits the search query string whenever it changes
- `suggestionsChanged`: Emits the suggestions as an ordered list of matched search terms whenever the suggestions are updated

### Example

In the following example, we have a fuzzy search box to search for a predefined set of usernames.
We want to retrieve the closest matching usernames whenever the user changes their search query.
The component looks like this:

```javascript
export class ExampleComponent {
  currentSuggestions: string[] = [];
  searchTerms = ['thijsfranck', 'wombach', 'mahi'];
}
```

And the html template looks like this:

```html
<models4insight-fuzzy-search-input [terms]="searchTerms" (suggestionsChanged)="currentSuggestions = $event"></models4insight-fuzzy-search-input>
```

Now, whenever the suggestions are updated, the component can access them via the `currentSuggestions` property.
