/**
 * Returns a `Generator` of all unique pairs of elements from the given `iterable`.
 * @param iterable The collection of which to find all unique element pairs.
 */
export function combinations<T>(iterable: Iterable<T>): Generator<[T, T]>;
/**
 * Returns a `Generator` of all unique combinations with the given `length` of elements from the given `iterable`.
 * @param iterable The collection of which to find all unique element combinations with the given `length`.
 * @param length A positive number indicating the desired length of the returned combinations
 */
export function combinations<T>(
  iterable: Iterable<T>,
  length: number
): Generator<T[]>;
export function* combinations<T>(
  iterable: Iterable<T>,
  length = 2
): Generator<T[]> {
  // If the desired length is 0, yield nothing
  if (length === 0) return;

  // Keep a record of the items we've seen so far to cut down on processing and avoid duplicate combinations
  const seenItems = new Set<T>();

  for (const currentItem of iterable) {
    if (seenItems.has(currentItem)) continue;
    if (length === 1) yield [currentItem];

    // Concatenate the current item with combinations of the items that we've seen so far
    // This will eventually result in all combinations for the current item
    // The recursion stops when the desired length reaches 0
    for (const combination of combinations(seenItems, length - 1)) {
      yield [...combination, currentItem];
    }

    seenItems.add(currentItem);
  }
}
