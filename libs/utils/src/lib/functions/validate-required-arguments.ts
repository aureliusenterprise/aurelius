import { Dictionary, isNil } from 'lodash';

/**
 * Throws an error if any of the given `args` cannot be validated.
 * By default, checks whether any argument is `null` or `undefined`.
 *
 * Use this function to check the required parameters of any function, such as an API call.
 *
 * @example function exampleApiCall(
 *            requiredArgumentA: string,
 *            requiredArgumentB: number,
 *            options: ExampleApiCallOptions = {}
 *          ) {
 *            // Validate the required arguments for the API call before we do anything else.
 *            // By passing the `arguments` variable, we check all function parameters, including `options`.
 *            // This works since `options` has a default value.
 *            validateRequiredArguments(arguments, 'exampleApiCall');
 *
 *            // If not all parameters are required, you can validate a subset by passing an array or an object.
 *            // In the example below, we exclude `requiredArgumentB` and `options` from the check.
 *            validateRequiredArguments([requiredArgumentA], 'exampleApiCall');
 *            validateRequiredArguments({requiredArgumentA}, 'exampleApiCall');
 *          }
 *
 *          // Let's now call `exampleApiCall` with null as the first parameter.
 *          // This results in an error telling us the parameter at index 0 was invalid.
 *          exampleApiCall(null, 0);
 *          // -> Error: Required parameter 0 was null when calling exampleApiCall.
 */
export function validateRequiredArguments(
  /** The arguments to validate. */
  args: Dictionary<any>,
  /**
   * The name of the function to which the arguments belong.
   * Passing the function name ensures a meaningful error message from uglified code.
   */
  calleeName: string,
  /**
   * The function used to validate each of the given arguments.
   * It should return `true` if the given argument is invalid.
   * By default, checks whether the given argument is `null` or `undefined`.
   */
  isInvalidFn: (arg: any) => boolean = isNil
) {
  const invalidArgument = Object.entries(args).find(([, value]) =>
    isInvalidFn(value)
  );

  if (invalidArgument) {
    throw new Error(
      `Required parameter ${invalidArgument[0]} was ${invalidArgument[1]} when calling ${calleeName}.`
    );
  }
}
