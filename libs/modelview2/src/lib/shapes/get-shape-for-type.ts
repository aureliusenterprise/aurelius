import { defs } from './defs';
import { relations } from './relations';
import { shapes } from './shapes';
import {
  ConnectionStyleFunction,
  NodeShapeFunction,
  RelationDef,
} from './types';

export function getShapeForType(type: keyof typeof shapes): NodeShapeFunction {
  return shapes[type];
}

export function getRelationForType(
  type: keyof typeof relations
): ConnectionStyleFunction {
  return relations[type];
}

export function getDefForType(type: keyof typeof defs): RelationDef {
  return defs[type];
}
