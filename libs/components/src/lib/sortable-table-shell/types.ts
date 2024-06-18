import { Dictionary } from 'lodash';

/**
 * You have the option of truncating a column value, replacing either the start or end of any long values with ellipsis (`...`).
 */
export type SortableTableShellColumnTruncate = 'start' | 'end';

export interface SortableTableShellColumnConfig {
  /** Hint to display when hovering over the column name */
  description?: string;
  /** The name of the column to display on the page */
  displayName?: string;
  /** Whether or not the column should shrink to exactly fit its content */
  isNarrow?: boolean;
  /** Whether or not sorting should be disabled for this column */
  isStatic?: boolean;
  /** Whether or not the column represents a timestamp */
  isTimestamp?: boolean;
  /** You have the option of truncating a column value, replacing either the start or end of any long values with ellipsis (`...`). */
  truncate?: SortableTableShellColumnTruncate;
}

export type SortableTableShellConfig<
  T extends Dictionary<any> = Dictionary<any>
> = { readonly [R in keyof T]?: SortableTableShellColumnConfig };
