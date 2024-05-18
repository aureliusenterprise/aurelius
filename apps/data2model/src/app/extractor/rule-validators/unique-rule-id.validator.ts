import { flatten } from 'lodash';
import { ExtractorRule } from '../extractor-types';
import { ValidationError, ValidationErrorSeverity } from './validation-error';

/**
 * A duplicate id error describes an occurrence where the validator found two extractor rules with the same or equivalent identifiers.
 */
export class DuplicateRuleIdError implements ValidationError {
  public readonly severity: ValidationErrorSeverity =
    ValidationErrorSeverity.WARNING;

  constructor(
    public readonly rule: string,
    /** The rule with the duplicate id */
    public readonly otherRule: string
  ) {}

  get description() {
    return `The identifier for rule ${
      this.rule
    } overlaps with the identifier of rule ${this.otherRule}`;
  }
}

function extractorRuleIdComparator(
  rule: ExtractorRule,
  otherRule: ExtractorRule
): boolean {
  switch (rule.id_type) {
    case 'dynamic':
      return (
        otherRule.id_type === 'dynamic' &&
        rule.id_key === otherRule.id_key &&
        ((!rule.id_prefix && !otherRule.id_prefix) ||
          rule.id_prefix === otherRule.id_prefix)
      );
    case 'static':
      return (
        otherRule.id_type === 'static' && rule.id_value === otherRule.id_value
      );
  }
}

/**
 * This validator checks each combination of rules from the given ruleset for duplicate ids. Ids are considered duplicate if one of the following is true:
 *
 * - In case of a dynamic identifier, the rules are using the same or an equivalent combination of `id_key` and `id_prefix`.
 * - In case of a static identifier, the rules are using the same `id_value`.
 *
 * Returns a set of errors representing each combination of a duplicate id.
 *
 * In case of an id collision, the model extractor will use the last rule encountered using that identifier.
 * The implementation of this function reflects this by only searching forward from the index of each rule.
 *
 * As a result, the rule referenced in the error will always be to the left of the colliding rule.
 * You can use the returned errors to perform a reverse mapping to compile a matrix of all id collisions.
 */
export function uniqueRuleId(
  /** The ruleset that should be validated */
  rules: ExtractorRule[]
): DuplicateRuleIdError[] {
  const duplicateIdsByRule = rules
    .filter(rule => rule.include)
    .map((rule, index, includedRules) =>
      includedRules
        .slice(index + 1)
        .filter(otherRule => extractorRuleIdComparator(rule, otherRule))
        .map(otherRule => new DuplicateRuleIdError(rule.id, otherRule.id))
    );
  return flatten(duplicateIdsByRule);
}
