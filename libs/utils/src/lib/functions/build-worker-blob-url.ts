declare var window: any;

/**
 * Helper function to create an object URL for the given function.
 * Useful for executing the given function as a web worker.
 * Use this as a workaround only if native web worker compilation with Angular is not available, e.g. in libraries.
 *
 * @param workerFunction The function for which to create an object url
 */
export function buildWorkerBlobURL(workerFunction: Function): string {
  const functionName = workerFunction.name;

  // Make sure code starts with "function()"
  // Chrome, Firefox: "[`functionName`](){...}", Safari: "function [`functionName`](){...}"
  // we need an anonymous function: "function() {...}"
  const functionAsString = workerFunction.toString().replace(/^function +/, '');

  // Convert to anonymous function
  const anonymousFunctionString = functionAsString.replace(
    functionName + '()',
    'function()'
  );

  // Self executing
  const workerString = '(' + anonymousFunctionString + ')();';

  // Build the worker blob
  const workerBlob = new Blob([workerString], { type: 'text/javascript' });

  const workerBlobUrl = window.URL.createObjectURL(workerBlob);
  return workerBlobUrl;
}
