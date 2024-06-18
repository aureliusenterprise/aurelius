import { isNil } from 'lodash';

/**
 * Returns a generator of all nodes and nested nodes in the given view as a flat sequence
 * @param view The view for which to get the nodes
 */
export function* getViewNodes(view: any): Generator<any> {
  const nodes = view?.['ar3_node'];

  if (isNil(nodes)) return;

  for (const node of nodes) {
    yield node;
    if ('ar3_node' in node) {
      yield* getViewNodes(node);
    }
  }
}
