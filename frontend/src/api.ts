import type { paths } from './api_types';
import { store } from './store/store';

/* =========================
 * OpenAPI Type-safe POST API
 * ========================= */

type PostRequest<P extends keyof paths> = paths[P]['post'] extends {
  requestBody: { content: { 'application/json': infer R } };
}
  ? R
  : never;

type PostResponse<P extends keyof paths> = paths[P]['post'] extends {
  responses: { 200: { content: { 'application/json': infer R } } };
}
  ? R
  : never;

export async function postAPI<P extends keyof paths>(
  path: P,
  body: PostRequest<P>
): Promise<PostResponse<P>> {
  const token = store.getState().jwtToken;

  const res = await fetch(path, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...(token !== null ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    throw await res.json();
  }

  return res.json() as Promise<PostResponse<P>>;
}
