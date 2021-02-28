type RequestIdleCallbackHandle = any;
type RequestIdleCallbackOptions = {
  timeout?: number;
};
type RequestIdleCallbackDeadline = {
  readonly didTimeout: boolean;
  timeRemaining: () => number;
};

function _reqIdle(
  callback: (deadline: RequestIdleCallbackDeadline) => void,
  opts?: RequestIdleCallbackOptions
): RequestIdleCallbackHandle {
  const start = Date.now();
  return window.setTimeout(function () {
    callback({
      didTimeout: false,
      timeRemaining: function () {
        return Math.max(0, 50 - (Date.now() - start));
      },
    });
  }, 1);
}
const _cancelIdle = window.clearTimeout.bind(window);

type CancelIdleCallback = (handle: number | undefined) => void;

export const rIC = window.requestIdleCallback || _reqIdle;
export const cIC: CancelIdleCallback = window.cancelIdleCallback || _cancelIdle;

window.requestIdleCallback = window.requestIdleCallback || _reqIdle;
window.cancelIdleCallback = window.cancelIdleCallback || _cancelIdle;

declare global {
  interface Window {
    requestIdleCallback: (
      callback: (deadline: RequestIdleCallbackDeadline) => void,
      opts?: RequestIdleCallbackOptions
    ) => RequestIdleCallbackHandle;
    cancelIdleCallback: (handle: RequestIdleCallbackHandle) => void;
  }
}
