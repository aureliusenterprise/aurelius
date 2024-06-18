/**
 * Returns a new object that represents the union between a and b. Nested objects are unified, nested lists are extended.
 */
export function union<A, B>(
  /** The base object */
  a: A,
  /** The other object */
  b: B,
  /** Whether or not to overwrite properties that exist in both a and b in case of a primitive value or non-matching types */
  overwrite = true
): A & B {
  // Make a shallow copy of the base object
  const result = Object.assign({}, a) as A;

  // Iterate over the keys in the other object and assign its values to the result object
  Object.keys(b).forEach((key: string) => {
    const newValue = b[key];

    // If the property already exists in the result object...
    if (result.hasOwnProperty(key)) {
      const currentValue = result[key];

      // If the types between A and B don't match, or if the value is a primitive...
      if (
        Object(newValue) !== newValue ||
        newValue.constructor !== currentValue.constructor
      ) {
        if (overwrite) {
          result[key] = newValue;
        }
      }

      // Else, if the value is an array
      else if (Array.isArray(newValue)) {
        result[key] = currentValue.concat(newValue);
      }

      // Else, if the value is a set
      else if (newValue instanceof Set) {
        result[key] = new Set([Array.from(currentValue), Array.from(newValue)]);
      }

      // Else, if the value is a random object
      else {
        result[key] = union(currentValue, newValue);
      }
    }

    // Otherwise simply assign the value
    else {
      result[key] = newValue;
    }
  });

  return result as A & B;
}
