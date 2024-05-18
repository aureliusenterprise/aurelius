import { flatten, isEqual, uniq, uniqWith } from 'lodash';
import { DefinitionType, ExtractorRule, SuggestedRelation } from '../extractor-types';
import { ValidationError, ValidationErrorSeverity } from './validation-error';

/**
 * An element not suggested error describes an occurrence where the validator found an element which does not match any current suggestion.
 */
export class ElementNotSuggestedError implements ValidationError {
  public readonly severity: ValidationErrorSeverity =
    ValidationErrorSeverity.INFO;

  constructor(
    public readonly rule: string,
    public readonly referencedColumn: string
  ) {}

  get description() {
    return `Column ${
      this.referencedColumn
    } used as this element's identifier does not match any suggestion.`;
  }
}

/**
 * A relationship not suggested error describes an occurrence where the validator found a relationship which does not match any current suggestion.
 */
export class RelationshipNotSuggestedError implements ValidationError {
  public readonly severity: ValidationErrorSeverity =
    ValidationErrorSeverity.INFO;

  constructor(
    public readonly rule: string,
    public readonly referencedSource: string,
    public readonly referencedTarget: string
  ) {}

  get description() {
    return `The combination of source ${this.referencedSource} and target ${
      this.referencedTarget
    } does not match any suggested relationship.`;
  }
}

/**
 * This validator checks for every element and relationship rule in the given ruleset whether or not there is any suggestion for which one of the following is true:
 *
 * - In case of an element rule, its `id_type` is dynamic and its `id_key` matches the source or target of any of the suggested relationships
 * - In case of a relationship rule, the tuple [`source`, `target`] of the rule matches with the source and target of any of the suggested relationships.
 *
 * Returns a set of validation errors representing every occurrence where neither of the above was true.
 */
export function ruleSuggested(
  /** The set of rules which should be validated */
  rules: ExtractorRule[],
  /** The set of suggested relationships to validate the rules against */
  suggestions: SuggestedRelation[]
) {
  /*
   * A set of all suggested combinations of columns.
   * Since suggestions are symmetrical, add both a tuple of source to target, and target to source.
   */
  const transitions = uniqWith(
    flatten(
      suggestions.map(suggestion => [
        [suggestion.source, suggestion.target],
        [suggestion.target, suggestion.source]
      ])
    ),
    isEqual
  );

  // A set of suggested columns
  const columns = uniq(flatten(transitions));

  const rulesWithoutSuggestion = rules
    .filter(
      rule =>
        rule.include &&
        [DefinitionType.ELEMENT, DefinitionType.RELATION].includes(rule.type)
    )
    .reduce(
      (acc, rule) => {
        switch (rule.type) {
          case DefinitionType.ELEMENT:
            if (rule.id_type === 'dynamic' && !columns.includes(rule.id_key)) {
              return [
                ...acc,
                new ElementNotSuggestedError(rule.id, rule.id_key)
              ];
            }
            return acc;
          case DefinitionType.RELATION:
            if (!transitions.includes([rule.source, rule.target])) {
              return [
                ...acc,
                new RelationshipNotSuggestedError(
                  rule.id,
                  rule.source,
                  rule.target
                )
              ];
            }
            return acc;
          default:
            return acc;
        }
      },
      [] as ValidationError[]
    );
  return rulesWithoutSuggestion;
}
