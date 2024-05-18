import { flatten } from 'lodash';
import { DefinitionType, ExtractorRule, RelationshipDefinition } from '../extractor-types';
import { ValidationError, ValidationErrorSeverity } from './validation-error';

/**
 * An unmapped relationship endpoint error describes an occurrence where the validator found an endpoint reference which does not map to any known rule id.
 */
export interface UnmappedRelationshipEndpointError extends ValidationError {
  /** The id of the rule representing the unknown endpoint */
  readonly unmappedEndpoint: string;
}

/**
 * An unmapped relationship source error describes an occurrence where the validator found a source reference which does not map to any known rule id.
 */

export class UnmappedRelationshipSourceError
  implements UnmappedRelationshipEndpointError {
  public readonly severity: ValidationErrorSeverity =
    ValidationErrorSeverity.ERROR;

  constructor(
    public readonly rule: string,
    public readonly unmappedEndpoint: string
  ) {}

  get description() {
    return `The source for this relationship is mapped to rule ${
      this.unmappedEndpoint
    }, but this does not match with any known element rules`;
  }
}

/**
 * An unmapped relationship target error describes an occurrence where the validator found a target reference which does not map to any known rule id.
 */
export class UnmappedRelationshipTargetError
  implements UnmappedRelationshipEndpointError {
  public readonly severity: ValidationErrorSeverity =
    ValidationErrorSeverity.ERROR;

  constructor(
    public readonly rule: string,
    public readonly unmappedEndpoint: string
  ) {}

  get description() {
    return `The target for this relationship is mapped to rule ${
      this.unmappedEndpoint
    }, but this does not match with any known element rules`;
  }
}

/**
 * This validator check for every relationship in the given ruleset whether or not the rules referenced as source and target by this relationship are known.
 * A relationship endpoint is known if a rule with the referenced id exists in the given ruleset.
 *
 * Returns a set of errors representing every occurrence of an unknown endpoint reference.
 */
export function mappedRelationshipEndpoints(
  /** The set of rules which should be validated */
  rules: ExtractorRule[]
): UnmappedRelationshipEndpointError[] {
  const ruleIds = rules.map((rule: ExtractorRule) => rule.id);
  const relationshipsWithUnmappedEndpoints = rules
    .filter(
      (rule: ExtractorRule) =>
        rule.include && rule.type === DefinitionType.RELATION
    )
    .map((rule: RelationshipDefinition) => {
      const result = [] as UnmappedRelationshipEndpointError[];
      if (!ruleIds.includes(rule.source)) {
        result.push(new UnmappedRelationshipSourceError(rule.id, rule.source));
      }
      if (!ruleIds.includes(rule.target)) {
        result.push(new UnmappedRelationshipTargetError(rule.id, rule.target));
      }
      return result;
    });
  return flatten(relationshipsWithUnmappedEndpoints);
}
