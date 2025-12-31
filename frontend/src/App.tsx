import React, { useEffect } from 'react';
import { Provider, useSelector } from 'react-redux';

import DashboardLayout from './components/DashboardLayout';
import ErrorPage from './pages/ErrorPage';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import {
  actions,
  getCurrentRoute,
  RootState,
  useAppDispatch,
} from './store/store';
import { store } from './store/store';
import { initUser } from './store/transitions';
import { Route } from './types';

const AppContent: React.FC = () => {
  const dispatch = useAppDispatch();

  const route = useSelector((state: RootState) => {
    return state.route;
  });

  useEffect(() => {
    const initializeApp = async () => {
      if (route == Route.Error) {
        return;
      }
      await initUser();
    };

    initializeApp();
  }, []);

  useEffect(() => {
    const handleRouteChange = () => {
      dispatch(actions.setCurrentRoute(getCurrentRoute()));
    };

    window.addEventListener('popstate', handleRouteChange);
    return () => window.removeEventListener('popstate', handleRouteChange);
  }, []);

  const divClassNames = 'h-full w-full';
  return (
    <>
      <DashboardLayout>
        <div
          className={`${divClassNames} ${route === Route.Home ? 'block' : 'hidden'}`}
        >
          <HomePage />
        </div>
        <div
          className={`${divClassNames} ${route === Route.Login ? 'block' : 'hidden'}`}
        >
          <LoginPage />
        </div>
        <div
          className={`${divClassNames} ${route === Route.Error ? 'block' : 'hidden'}`}
        >
          <ErrorPage />
        </div>
      </DashboardLayout>
    </>
  );
};

const App: React.FC = () => {
  return (
    <Provider store={store}>
      <AppContent />
    </Provider>
  );
};

export default App;
