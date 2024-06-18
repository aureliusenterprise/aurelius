declare var window: any;

/**
 * Returns `true` if the current User Agent is a Microsoft Edge (non-chromium) variant.
 */
export function userAgentIsEdge() {
  return ['Edge/'].some(
    (userAgent) => window && window.navigator.userAgent.includes(userAgent)
  );
}
