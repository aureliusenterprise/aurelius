import MultiMap from 'mnemonist/multi-map';

/**
 * A multi-map implementation that also maintains a shadow copy mapping all values to their respective keys.
 */
export class BidirectionalMultiMap<K, V> {
  readonly mapping: MultiMap<K, V>;
  readonly inverse: MultiMap<V, K>;

  constructor(container: ArrayConstructor | SetConstructor = Array) {
    this.mapping = new MultiMap(container);
    this.inverse = new MultiMap(container);
  }

  clear() {
    this.inverse.clear();
    this.mapping.clear();
  }

  delete(key: K) {
    for (const value of this.mapping.get(key) ?? []) {
      this.inverse.remove(value, key);
    }
    return this.mapping.delete(key);
  }

  remove(key: K, value: V) {
    this.inverse.remove(value, key);
    return this.mapping.remove(key, value);
  }

  set(key: K, value: V) {
    this.inverse.set(value, key);
    return this.mapping.set(key, value);
  }
}
