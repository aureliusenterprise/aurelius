declare var window: any;

/**
 * Returns `true` if the current User Agent is an Internet Explorer variant.
 */
export function userAgentIsInternetExplorer() {
  return ['MSIE ', 'Trident/'].some(
    (userAgent) => window && window.navigator.userAgent.includes(userAgent)
  );
}
