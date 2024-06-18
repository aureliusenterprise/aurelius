import { isEqual } from 'lodash';

/**
 * Sequence based on an Iterator that supports sequential operations similar to an `Array`.
 *
 * To perform a computation, stream operations are composed into a stream pipeline.
 * A stream pipeline consists of:
 *
 * - A single source (e.g. a `Function` that supplies an `Iterable`, or a `Generator` function)
 * - Zero or more intermediate operations (which transform the `Stream` into another `Stream`)
 * - A single terminal operation (which produces a result or side-effect)
 *
 * It is not required to end a stream pipeline with a terminal operation provided by this class.
 * A `Stream` can be consumed like any regular `Iterable`, e.g. using a `for...of` loop.
 *
 * Streams are lazy.
 * Computation on the source data is only performed when the terminal operation is initiated.
 * Source elements are consumed only as needed.
 */
export class Stream<T> implements Iterable<T> {
  public [Symbol.iterator]: () => Iterator<T>;

  constructor(source: () => Iterator<T>) {
    this[Symbol.iterator] = source;
  }

  /**
   * Returns a `Stream` consisting of all elements of the given `source`.
   * @param source The source of the stream.
   */
  static from<T>(source: Iterable<T>): Stream<T> {
    function* from() {
      yield* source;
    }
    return new Stream<T>(from);
  }

  /**
   * Reduces the elements of this stream using the given `collector`.
   * @param collector the `Function` describing the reduction
   */
  collect<R>(collector: (stream: this) => R): R {
    return collector(this);
  }

  /**
   * Returns a lazily concatenated `Stream` whose elements are all the elements of this stream followed by all the elements of the given `iterables`.
   * @param iterables The iterables that should be concatenated to this stream.
   */
  concat<R>(...iterables: Iterable<R>[]) {
    function* concat(base: Iterable<T>) {
      yield* base;
      for (const iterable of iterables) {
        yield* iterable;
      }
    }
    return new Stream(() => concat(this));
  }

  /**
   * Returns a `Stream` consisting of the unique elements of this stream.
   * @param comparator Function that returns `true` if two stream elements are the same. Defaults to `isEqual`.
   */
  distinct(comparator: (item: T, other: T) => boolean = isEqual) {
    function* distinct(iterable: Iterable<T>) {
      const seenItems = [];
      for (const item of iterable) {
        const hasBeenSeen = seenItems.some((seen) => comparator(item, seen));
        if (!hasBeenSeen) {
          yield item;
          seenItems.push(item);
        }
      }
    }
    return new Stream(() => distinct(this));
  }

  /**
   * Returns whether all elements of this stream match the given `predicate`.
   * @param predicate The test condition.
   */
  every(predicate: (item?: T) => boolean): boolean {
    for (const item of this) {
      if (!predicate(item)) {
        return false;
      }
    }
    return true;
  }

  /**
   * Returns a `Stream` consisting of the elements of this stream that match the given `predicate`.
   * @param predicate The filter condition.
   */
  filter(predicate: (item?: T) => boolean): Stream<T> {
    function* filter(iterable: Iterable<T>) {
      for (const item of iterable) {
        if (predicate(item)) {
          yield item;
        }
      }
    }
    return new Stream(() => filter(this));
  }

  /**
   * Returns the first element of this stream that matches the given `predicate`.
   * @param predicate The test condition.
   */
  find(predicate: (item: T) => boolean): T {
    for (const item of this) {
      if (predicate(item)) {
        return item;
      }
    }
  }

  /**
   * Returns the first element of this stream.
   */
  first(): T {
    for (const item of this) {
      return item;
    }
  }

  /**
   * Returns a `Stream` consisting of the results of replacing each element of this stream with the contents of a mapped `Iterable` produced by applying the provided `projection` to each element.
   * @param projection The function to apply to each element of this stream.
   */
  flatMap<R>(projection: (item?: T) => Iterable<R>): Stream<R> {
    function* map(iterable: Iterable<T>) {
      for (const item of iterable) {
        yield* projection(item);
      }
    }
    return new Stream(() => map(this));
  }

  /**
   * Performs an action for each element of this stream.
   * @param effect The action to perform.
   */
  forEach(effect: (item?: T) => void) {
    for (const item of this) {
      effect(item);
    }
  }

  /**
   * Retruns a `Stream` consisting of the results of applying the given `projection` to the elements of this stream.
   * @param projection The function to apply to each element of this stream.
   */
  map<R>(projection: (item?: T) => R): Stream<R> {
    function* map(iterable: Iterable<T>) {
      for (const item of iterable) {
        yield projection(item);
      }
    }
    return new Stream(() => map(this));
  }

  /**
   * Returns whether no elements of this stream match the given `predicate`.
   * @param predicate The test condition.
   */
  none(predicate: (item: T) => boolean): boolean {
    for (const item of this) {
      if (predicate(item)) {
        return false;
      }
    }
    return true;
  }

  /**
   * Accumulates the elements of this stream.
   * @param accumulator The function that accumulates the elements of the stream.
   * @param startWith The starting value of the accumulation.
   */
  reduce<R>(accumulator: (acc: R, item: T) => R, startWith: R): R {
    let accumulation = startWith;
    for (const item of this) {
      accumulation = accumulator(accumulation, item);
    }
    return accumulation;
  }

  /**
   * Returns a `Stream` consisting of the remaining elements of this stream after discarding the first given `number` of elements.
   * @param number The number of elements to skip.
   */
  skip(number: number): Stream<T> {
    function* skip(iterable: Iterable<T>) {
      let i = 0;
      for (const item of iterable) {
        if (i >= number) {
          yield item;
        }
        i++;
      }
    }
    return new Stream(() => skip(this));
  }

  /**
   * Returns whether any elements of this stream match the given `predicate`.
   * @param predicate The test condition.
   */
  some(predicate: (item?: T) => boolean): boolean {
    for (const item of this) {
      if (predicate(item)) {
        return true;
      }
    }
    return false;
  }

  /**
   * Returns a `Stream` consisting of the first given `number` of elements of this stream.
   * @param number The number of elements to take.
   */
  take(number: number): Stream<T> {
    function* take(iterable: Iterable<T>) {
      let i = 0;
      for (const item of iterable) {
        yield item;
        i++;
        if (i >= number) {
          break;
        }
      }
    }
    return new Stream(() => take(number > 0 ? this : []));
  }

  /**
   * Returns a `Stream` consisting of the first elements of this stream that match the given `predicate`.
   * @param predicate The test condition.
   */
  takeUntil(predicate: (item?: T) => boolean): Stream<T> {
    function* takeUntil(iterable: Iterable<T>) {
      for (const item of iterable) {
        if (predicate(item)) {
          break;
        }
        yield item;
      }
    }
    return new Stream(() => takeUntil(this));
  }

  /**
   * Returns a `Stream` consisting of the elements of this stream, additionally performing the given `effect` on each element.
   * @param effect The effect to perform.
   */
  tap(effect: (item?: T) => void) {
    function* tap(iterable: Iterable<T>) {
      for (const item of iterable) {
        effect(item);
        yield item;
      }
    }
    return new Stream(() => tap(this));
  }

  /**
   * Retruns an `Array` containing the elements of this stream.
   */
  toArray(): T[] {
    return Array.from(this);
  }
}
