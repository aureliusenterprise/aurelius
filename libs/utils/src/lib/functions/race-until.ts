/**
 * Returns a new `Promise` which resolves when either:
 * - One of the given `promises` resolves with a value which meets the given `predicate`. In this case, the resolved value is returned.
 * - None of the given `promises` resolves with a value which meets the given `predicate`. In this case, a default value (`null` by default) is returned instead.
 *
 * If one of the given `promises` rejects before a value which meets the given `predicate` is found, the result is rejected overall.
 */
export async function raceUntil<T>(
  /** The promises to resolve */
  promises: Promise<T>[],
  /** The condition which the resolved value should fulfill */
  predicate: (value: T) => boolean,
  /** The value to return if none of the given promises resolves with a value which meets the given predicate */
  defaultValue: T = null
): Promise<T> {
  const conditionalPromises = promises.map(
    async (promise) =>
      new Promise<T>((resolve, reject) =>
        promise.then((value) => predicate(value) && resolve(value), reject)
      )
  );

  return Promise.race<T>([
    ...conditionalPromises,
    Promise.all(promises).then(() => defaultValue),
  ]);
}
