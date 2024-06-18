# UserSearchInput

This module provides the `models4insight-user-search-input` component, which allows the user to query for the user info of another user if they know the email address with which they registered. After the query string has changed, it makes a request to the users API. This API returns a result only if the full email address was given. This limits the possibility of crawling our users database.

The `models4insight-user-search-input` provides the following outputs:

- `suggestions`: Emits a list of `UserSearch` objects whenever the suggestions are updated
