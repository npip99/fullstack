import { configureStore, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { useDispatch } from 'react-redux';

import { AppState, isRoute, LoggedInState, Route } from '../types';

export const getCurrentRoute = (): Route => {
  const currentPath = window.location.pathname.slice(1);
  if (isRoute(currentPath)) {
    return currentPath;
  } else {
    let inferredRoute = Route.Home;

    // Example of redirecting to login if not logged in
    // if (localStorage.getItem('jwt_token') === null) {
    //   inferredRoute = Route.Login;
    // }

    // Preserve query parameters when redirecting to inferred route
    const queryString = window.location.search;
    history.pushState(null, '', '/' + inferredRoute + queryString);
    return inferredRoute;
  }
};

const initialState: AppState = {
  jwtToken: localStorage.getItem('jwt_token'),
  loggedInState: null,
  route: getCurrentRoute(),
};

const appSlice = createSlice({
  name: 'app',
  initialState: initialState as AppState,
  reducers: {
    setCurrentRoute: (state, action: PayloadAction<Route>) => {
      state.route = action.payload;
    },
    login: (state, action: PayloadAction<{ loggedInState: LoggedInState }>) => {
      state.loggedInState = action.payload.loggedInState;
    },
    logout: (state) => {
      console.log('Logging Out!');
      localStorage.removeItem('jwt_token');
      state.loggedInState = null;
      state.jwtToken = null;
    },
  },
});

export const actions = appSlice.actions;
export const store = configureStore({
  reducer: appSlice.reducer,
});

export type RootState = ReturnType<typeof store.getState>;

export type AppDispatch = typeof store.dispatch;
export const useAppDispatch = () => useDispatch<AppDispatch>();
