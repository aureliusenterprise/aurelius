export enum ActionType {
  RESET = 'RESET',
  SET = 'SET',
  UPDATE = 'UPDATE',
  DELETE = 'DELETE',
}

export interface SetAction<T> {
  type: ActionType.SET;
  description: string;
  payload: T;
}

export interface UpdateAction<T> {
  type: ActionType.UPDATE;
  description: string;
  path: (string | number)[];
  payload: T;
}

export interface DeleteAction {
  type: ActionType.DELETE;
  description: string;
  path: (string | number)[];
}

export interface ResetAction {
  type: ActionType.RESET;
  description: string;
}

// You can extend Action by piping in additional types, e.g:
// export type ExtendedAction<T> = Action<T> | MyAction<T>
export type Action<T> =
  | SetAction<T>
  | UpdateAction<T>
  | DeleteAction
  | ResetAction;
