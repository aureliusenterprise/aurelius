/** Custom error base class that allows instanceof checking */
export abstract class CustomError extends Error {
  constructor(message: string) {
    super(message);
    // Set the prototype explicitly
    Object.setPrototypeOf(this, new.target.prototype);
  }
}
