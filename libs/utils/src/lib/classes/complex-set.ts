import { isEqual, uniqWith } from 'lodash';

export class ComplexSet<T> {
  private array: T[] = [];

  /**
   * Represents a `Set` with a custom comparator.
   * This allows you to create sets of complex objects.
   * The `isEqual` method from `lodash` is used by default.
   *
   * **IMPORTANT**: For primitive values, the built-in `Set` object is more efficient.
   */
  constructor(
    /**
     * This method determines whether or not an item is already present in the set.
     * Defaults to the `isEqual` method from `lodash`.
     */
    private comparator: (item: T, otherItem: T) => boolean = isEqual
  ) {}

  /**
   * Adds one or more additional values to the set.
   * @param value the value(s) which should be added to the set.
   */
  add(value: T | T[]) {
    if (!Array.isArray(value)) {
      value = [value];
    }
    this.array = uniqWith([...this.array, ...value], this.comparator);
  }

  /**
   * Returns the set as an an array of unique items
   */
  get items() {
    return this.array;
  }
}
