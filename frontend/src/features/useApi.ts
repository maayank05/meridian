import { useCallback, useEffect, useState } from "react";
import { ApiError } from "../services/api";

export type ApiState<T> =
  | { status: "loading" }
  | { status: "error"; error: ApiError }
  | { status: "success"; data: T };

/**
 * Fetch whenever `key` changes; `retry` re-runs the request. "loading" is derived (the stored result belongs to
 * an older request), so no state is set synchronously inside the effect.
 */
export function useApi<T>(loader: () => Promise<T>, key: string): ApiState<T> & { retry: () => void } {
  const [attempt, setAttempt] = useState(0);
  const requestKey = `${key}#${attempt}`;
  const [result, setResult] = useState<{ key: string; state: ApiState<T> } | null>(null);

  useEffect(() => {
    let active = true;
    loader()
      .then((data) => active && setResult({ key: requestKey, state: { status: "success", data } }))
      .catch((e: unknown) =>
        active && setResult({ key: requestKey, state: { status: "error", error: e instanceof ApiError ? e : new ApiError(0, String(e)) } }),
      );
    return () => {
      active = false;
    };
    // loader identity changes every render; requestKey captures its inputs
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [requestKey]);

  const retry = useCallback(() => setAttempt((a) => a + 1), []);
  const state: ApiState<T> = result && result.key === requestKey ? result.state : { status: "loading" };
  return { ...state, retry };
}
