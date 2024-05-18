/**
 * Describes a degree of severity for a validation error
 */
export enum ValidationErrorSeverity {
  /** Does not affect the extraction result, but may not be intended by the user. */
  INFO = 'info',
  /** Affects the extraction result, but a model can still be extracted. */
  WARNING = 'warning',
  /** Prevents a model from being extracted. */
  ERROR = 'error'
}

/**
 * A validation error describes some inconsistency in an extractor rule.
 * It contains a reference to the faulty rule, as well as a textual description of the inconsistency.
 * All extractor rule validators should return an implementation of this class.
 */
export interface ValidationError {
  /** A reference to the id of the rule this error is associated with. */
  readonly rule: string;
  /** A textual description of the rule inconsistency. */
  readonly description: string;
  /** The severity type of this error */
  readonly severity: ValidationErrorSeverity;
}
