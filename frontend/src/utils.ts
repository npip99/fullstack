export function unwrap<T>(value: T | undefined | null): T {
  if (value === undefined || value == null) {
    throw new Error('found undefined or null where non-null was expected');
  } else {
    return value;
  }
}

let redirecting = false;

export const redirect = (newUrl: string) => {
  redirecting = true;

  // Pass invite token
  const urlParams = new URLSearchParams(window.location.search);
  const inviteParam = urlParams.get('invite');
  if (!newUrl.includes('?') && inviteParam) {
    newUrl += `?invite=${encodeURIComponent(inviteParam)}`;
  }

  window.location.href = newUrl;
};

export const isRedirecting = () => redirecting;
