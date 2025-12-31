/* ============================
 * Reusable Interfaces
 * ============================ */

export type Loadable<T> =
  | { status: 'idle' } // Initial state
  | { status: 'loading'; taskId: string; prevData?: T } // When loading, include a task ID
  | { status: 'error'; message: string } // If an error occurs
  | { status: 'success'; data: T }; // Successfully loaded data

export function getTaskId<T>(loadable?: Loadable<T> | null): string | null {
  if (!loadable) {
    return null;
  }
  switch (loadable.status) {
    case 'loading':
      return loadable.taskId;
    default:
      return null;
  }
}

/* ============================
 * Account State
 * ============================ */

export interface Account {
  id: string;
  name: string;
  email: string | null;
  profilePicture: string | null;
}

/* ============================
 * App State
 * ============================ */

export interface LoggedInState {
  account: Account;
}

export const Route = {
  Home: 'home',
  Login: 'login',
  Error: 'error',
} as const;
export type Route = (typeof Route)[keyof typeof Route];

const ALL_ROUTES = new Set<string>(Object.values(Route));
export const isRoute = (value: string): value is Route => {
  return ALL_ROUTES.has(value);
};

export interface AppState {
  route: Route;
  jwtToken: string | null;
  loggedInState: LoggedInState | null;
}
