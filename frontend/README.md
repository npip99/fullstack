# Frontend Methodology

This document describes the coding methodology for the frontend. In particular, the approach is very strictly typed and focuses on employing pure functional programming wherever possible.

At a high level, the frontend state is a _global singleton state_. The ReactJS code declaratively renders this state so that it is viewable by the end user. Additionally, the ReactJS will expose buttons and other input methods that will trigger _transitions_ that modify the global singleton state (Therefore causing a re-render loop of the React).

Details and organizational structure are explained below.

## Terminology

**state type** - The shape $S$ (i.e. type) of the state. All possible configurations of this type, represent all valid DFA nodes.

**state** - The application data. I.e., a specific DFA node.

**substate** - A "subtree" of state. E.g., if $S = X \times Y \times Z$, then a substate could have type $X$.

**initial state** - The first state $S_0$, is induced by a function $f_{init}: (p, l) \rightarrow S$, where $p$ is the url path (i.e. the url bar at the top), and $l$ is the Javascript localStorage (Currently only containing the login token `jwt_token`).

**reducer** - A function $f: (S, P) \rightarrow S$ that modifies the state. Reducers will have additional parameters $P$.

**store** - An object that holds the state, and protects the state by ensuring that you can only modify it with the list of valid reducers.

- I.e., similar, but not identical to, "encapsulation" in Java. Notably, this is a "singleton" pattern in the terminology of OOP.

**transition** - An asynchronous function that codifies a particular "long-running asynchronous action". A transition will often, but not always, occur in these steps:

- Step 1. Create a random uuid (called `task_id`)
- Step 2. Call a reducer so that the relevant substate is set to `Loading(task_id)`. The frontend will render the `Loading(*)` substate as a spinner or something. The `task_id` will be stored in the state, but ignored by the UI.
- Step 3. Dispatch a Backend API call, awaiting the response.
- Step 4. Upon receiving the API response, we call a reducer so that the state is `"UsefulData"` or `"<SomeError>"`, but ONLY if the substate is _still_ `Loading(task_id)`. If the state's `task_id` has changed or was no longer marked as `Loading`, then upon receiving the backend's api response, we give up / throw out the response / and do NOT modify the state at all.
  - The purpose of checking `task_id`, is for when the user is spamclicking a button, so that only the latest button click's results are shown (And they see a spinner thoroughout the duration of their spamclicking).

**view** - The "type" describing the set of valid HTML code.

**renderer** - A function that maps **states** to **views**. E.g., $f: S \rightarrow V$, where $S$ is our state, $f$ is our renderer, and $V$ is the **view** displaying the state to the User.

- In our code, $f$ is written as a React function (that itself calls react functions), and $V$ is the HTML DOM.

## Files

**types.ts** - Contains a specification of the **state type**

**store.ts** - Contains a list of valid **reducers**, and instantiates the global **store** instance. The instantiation occurs at the bottom, at

```typescript
export const store = configureStore({
  reducer: appSlice.reducer,
});
```

**transitions.ts** - The list of valid **transition** functions.

**\*.tsx** - The root `App.tsx` declares the function `AppContent`$: S \rightarrow V$, which is our renderer function. Our renderer could be written as one massive file, but for organization, it is split into many smaller `*.tsx` files, which define functions that are simply called by `AppContent` (creating a deep render call graph).

Additionally, the renderer will also render interactive buttons and text boxes, which will call **transition** functions if interacted with by the User. The transition functions will, naturally, asynchronously update the state in the background. Any such update to the state will automatically trigger a re-render of the view.

- A caveat to this explanation, is that there's actually an additional state/state type called the "UI State" and "UI State Type". This is for "micro state" adjustments, e.g. how when you hover over a button, it changes color. It would be arduous to include all UI State into the **state type**. You can create your own UI State with the `useState` react function, but this is usually discouraged - you should almost always use the global **state**. Examples where `useState` makes sense could be a UI form, which lets you modify your selection before eventually clicking "Submit", wherein "Submit" will actually call the **transition**.
