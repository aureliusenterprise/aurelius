import { difference } from 'lodash';
import { union } from './union';

interface UnionTest {
  primitive: number;
  object: { a?: string; b?: string };
  list: number[];
  differentType: string | number;
  additionalProperty?: boolean;
}

describe('union', () => {
  let _a: UnionTest = {
    primitive: 123,
    object: {
      a: 'a',
    },
    list: [1, 2, 3],
    differentType: '123',
  };
  let a: UnionTest;

  let _b: UnionTest = {
    primitive: 456,
    object: {
      b: 'b',
    },
    list: [4, 5, 6],
    differentType: 123,
    additionalProperty: true,
  };
  let b: UnionTest;

  let result: UnionTest;

  beforeEach(() => {
    a = Object.assign({}, _a);
    b = Object.assign({}, _b);
    result = union(a, b);
  });

  it('should not modify the source objects', () => {
    expect(a).toEqual(_a);
    expect(b).toEqual(_b);
  });

  it('should return an object that contains the keys in A and B', () => {
    expect(
      difference(
        Array.from(new Set([...Object.keys(a), ...Object.keys(b)])),
        Object.keys(result)
      ).length
    ).toEqual(0);
  });

  it('should concatenate list properties', () => {
    expect(result.list).toEqual(a.list.concat(b.list));
  });

  it('should merge nested objects', () => {
    expect(
      difference(
        Array.from(
          new Set([...Object.keys(a.object), ...Object.keys(b.object)])
        ),
        Object.keys(result.object)
      ).length
    ).toEqual(0);
  });

  it('should overwrite primitive values when overwrite is true', () => {
    expect(result.primitive).toEqual(b.primitive);
  });

  it('should overwrite non matching types when overwrite is true', () => {
    expect(result.differentType).toEqual(b.differentType);
  });

  it('should not overwrite primitive values when overwrite is false', () => {
    result = union(a, b, false);
    expect(result.primitive).toEqual(a.primitive);
  });

  it('should not overwrite non matching types when overwrite is false', () => {
    result = union(a, b, false);
    expect(result.differentType).toEqual(a.differentType);
  });
});
