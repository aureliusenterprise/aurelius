import { flatten } from 'lodash';
import { DefinitionType, ExtractorRule, ViewDefinition } from '../extractor-types';
import { ValidationError, ValidationErrorSeverity } from './validation-error';

/**
 * An unmapped view element error describes an occurrence where the validator found an element reference which does not map to any known rule id.
 */
export interface UnmappedViewElementError extends ValidationError {
  /** The id of the rule representing the unknown element */
  readonly unmappedElement: string;
}

/**
 * An unmapped view node error describes an occurrence where the validator found a reference to a node which does not map to any known rule id.
 */
export class UnmappedViewNodeError implements UnmappedViewElementError {
  public readonly severity: ValidationErrorSeverity =
    ValidationErrorSeverity.ERROR;

  constructor(
    public readonly rule: string,
    public readonly unmappedElement: string
  ) {}

  get description() {
    return `This view references node ${
      this.unmappedElement
    }, but this does not match with any known element rules`;
  }
}

/**
 * An unmapped view edge error describes an occurrence where the validator found a reference to an edge which does not map to any known rule id.
 */
export class UnmappedViewEdgeError implements UnmappedViewElementError {
  public readonly severity: ValidationErrorSeverity =
    ValidationErrorSeverity.ERROR;

  constructor(
    public readonly rule: string,
    public readonly unmappedElement: string
  ) {}

  get description() {
    return `This view references edge ${
      this.unmappedElement
    }, but this does not match with any known relationship rules`;
  }
}

/**
 * This validator check for every view in the given ruleset whether or not all rules referenced as nodes and edges by this view are known.
 * A view element is known if a rule with the referenced id exists in the given ruleset.
 *
 * Returns a set of errors representing every occurrence of an unknown element reference.
 */
export function mappedViewElements(
  /** The rules which should be validated */
  rules: ExtractorRule[]
): UnmappedViewElementError[] {
  const ruleIds = rules.map((rule: ExtractorRule) => rule.id);
  const viewsWithUnmappedElements = rules
    .filter((rule: ExtractorRule) => rule.include && rule.type === DefinitionType.VIEW)
    .map((rule: ViewDefinition) => {
      const unmappedViewElements = [
        rule.view_nodes
          .filter(node => !ruleIds.includes(node.rule))
          .map(node => new UnmappedViewNodeError(rule.id, node.rule)),
        rule.view_edges
          .filter(edge => !ruleIds.includes(edge.rule))
          .map(edge => new UnmappedViewEdgeError(rule.id, edge.rule))
      ];
      return flatten(unmappedViewElements);
    });
  return flatten(viewsWithUnmappedElements);
}
