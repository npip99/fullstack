import { postAPI } from '../api';
import { Account } from '../types';
import { actions, store } from './store';

// Fetch User

const fetchAccount = async (): Promise<Account> => {
  const account = await postAPI('/api/accounts/get-account', {});

  return {
    id: account.account.id,
    name: `${account.account.first_name} ${account.account.last_name}`.trim(),
    email: account.account.email,
    profilePicture: null,
  };
};

export const initUser = async (): Promise<void> => {
  const { jwtToken } = store.getState();
  if (!jwtToken) {
    store.dispatch(actions.logout());
    return;
  }

  let account;
  try {
    account = await fetchAccount();
  } catch (error) {
    console.error('Error loading app state:', error);
    store.dispatch(actions.logout());
    return;
  }

  store.dispatch(
    actions.login({
      loggedInState: {
        account,
      },
    })
  );
};
