# UserSearchModal

This module provides the `models4insight-user-search-modal` which implements a form for searching for users and adding users based on the suggestions returned. Whenever the current search query matches one or more users, the result is displayed in a table. The table shows the usernames and a button by which they can be added. Whenever a user is added, and event is triggered which can be consumed by the parent.

The `models4insight-user-search-modal` provides the following inputs:

- `currentUsers`: A list of user names of users who cannot be added

Further, it provides the following outputs:

- `user`: Emits a `UserSearch` object whenever the add button is clicked for a user
