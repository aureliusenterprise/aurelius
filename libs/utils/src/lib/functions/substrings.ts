export interface SubstringOptions {
  /** The minimum length of the substrings. Default is `1`. */
  minLength?: number;
  /** The maximum length of the substrings. Default is the length of the given `string`. */
  maxLength?: number;
}

/**
 * Returns all unique substrings of the given `string`. You can optionally specify a minimum and maximum substring length.
 * @param string The string for which to find all substrings.
 */
export function* substrings(
  string: string,
  { minLength = 1, maxLength = string.length }: SubstringOptions = {}
): Generator<string> {
  const seen = new Set<string>();
  for (let i = 0; i <= string.length - minLength; i++) {
    for (let j = i + minLength; j <= Math.min(maxLength, string.length); j++) {
      const substring = string.slice(i, j);
      if (!seen.has(substring)) {
        yield substring;
        seen.add(substring);
      }
    }
  }
}
