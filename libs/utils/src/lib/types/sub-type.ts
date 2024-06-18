type FilterFlags<Base, Condition> = {
  [Key in keyof Base]: Base[Key] extends Condition ? Key : never;
};

type AllowedNames<Base, Condition> = FilterFlags<Base, Condition>[keyof Base];

/**
 * Filters the available keys of a base type by a given type condition.
 * For example, SubType<Base, number>, returns a type with number values only.
 *
 * [Source](https://medium.com/dailyjs/typescript-create-a-condition-based-subset-types-9d902cea5b8c)
 */
export type SubType<Base, Condition> = Pick<
  Base,
  AllowedNames<Base, Condition>
>;
