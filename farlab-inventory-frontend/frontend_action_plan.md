---

Frontend Development Action Plan

Phase 1: Core Layout and Data Fetching
(Goal: Create a functional application shell that can display data from the
backend.)

- Task 1: Global State and Context

  - File: src/context/AppContext.jsx
  - Action: Create a React Context to manage the global state you defined:
    currentUser, searchQuery, isSearchActive, etc. This will make state
    accessible throughout the component tree without prop drilling.
  - File: src/App.jsx
  - Action: Wrap the application's routes with the new AppContext.Provider.

*Task 1.* creates a centralized place for the
  application's global state using React's Context API. This will allow any component to access or update shared data like the current user or the search query without passing props down through many levels.


- Task 2: Dynamic Navigation Tabs

  - File: src/components/NavigationTabs.jsx
  - Action:
    1.  Fetch the list of all instruments from the backend (GET /instruments).
    2.  Render a NavLink from react-router-dom for each instrument.
    3.  Style the active tab based on the URL's :instrumentType parameter.
    4.  Implement the "disabled/dimmed" appearance when isSearchActive is true
        (from context).

- Task 3: Displaying Instrument Parts

  - File: src/pages/InstrumentPage.jsx
  - Action:
    1.  Get the :instrumentType from the URL parameters.
    2.  Use this parameter to fetch the corresponding parts from the backend (GET
        /parts?instrument_name=...).
    3.  Pass the fetched parts data as a prop to the PartsTable component.
    4.  Handle loading and error states.

- Task 4: Creating the Parts Table
  - File: src/components/PartsTable.jsx
  - Action:
    1.  Receive the parts array as a prop.
    2.  Map over the array to render a PartItem component for each part.
    3.  Display a clean table header.
  - File: src/components/PartItem.jsx
  - Action:
    1.  Receive a single part object as a prop.
    2.  Render the details of the part in a table row (<tr>).

Phase 2: Search Functionality
(Goal: Implement the global, cross-instrument search feature.)

- Task 5: Building the Search Hooks

  - File: src/hooks/useDebounce.js
  - Action: Create a custom hook that takes a value and a delay, returning the
    debounced value. This is a standard and highly reusable hook.
  - File: src/hooks/useSearch.js
  - Action: Create a custom hook to encapsulate all search logic: making the API
    call, managing searchLoading state, and handling results.

- Task 6: Implementing the Search Box

  - File: src/components/SearchBox.jsx
  - Action:
    1.  Create a controlled input field whose value is tied to the searchQuery
        from our global context.
    2.  Implement the "clear" button, which becomes visible when searchQuery is
        not empty.
  - File: src/components/Header.jsx
  - Action: Integrate the SearchBox component into the header.

- Task 7: Displaying Search Results
  - File: src/components/SearchResults.jsx
  - Action:
    1.  This component will be conditionally rendered in Layout.jsx when
        isSearchActive is true.
    2.  It will receive the searchResults and searchLoading state from the global
        context.
    3.  It will display a loading spinner or the list of results.
    4.  Each result item should have a colored "tag" indicating which instrument
        it belongs to.

Phase 3: Authentication
(Goal: Implement user login, logout, and secure routing.)

- Task 8: Login Page and Authentication Service

  - File: src/pages/LoginPage.jsx
  - Action: Create a simple form to capture username and password.
  - File: src/utils/auth.js
  - Action: Create functions for login(username, password) and logout(). The
    login function will call the /auth/login endpoint, store the token using
    setAuthToken from our API utility, and also save it to localStorage.
  - File: src/App.jsx
  - Action: Add the /login route.

- Task 9: User Menu and Protected Routes
  - File: src/components/UserMenu.jsx
  - Action: Display the current user's name and a "Logout" button.
  - File: src/components/Header.jsx
  - Action: Integrate the UserMenu into the header.
  - File: src/components/ProtectedRoute.jsx
  - Action: Create a wrapper component that checks if a user is authenticated. If
    not, it redirects to the /login page. Use this to protect the main Layout.

Phase 4: Styling and Final Touches
(Goal: Apply CSS to match the professional, clean design specified.)

- Task 10: Global and Component-Specific Styles
  - Files: src/index.css, src/App.css, and new .css files for each component.
  - Action:
    1.  Define global styles, fonts, and color variables in index.css.
    2.  Implement the responsive layouts using CSS Grid and Flexbox.
    3.  Style each component to match the design, including hover states, active
        states, and the mobile hamburger menu.

---
