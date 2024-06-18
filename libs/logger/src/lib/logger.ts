/**
 * Simple logger system with the possibility of registering custom outputs.
 *
 * 4 different log levels are provided, with corresponding methods:
 * - debug   : for debug information
 * - info    : for informative status of the application (success, ...)
 * - warning : for non-critical errors that do not prevent normal application behavior
 * - error   : for critical errors that prevent normal application behavior
 *
 * Example usage:
 * ```
 * import { Logger } from 'app/core/logger.service';
 *
 * const log = new Logger('myFile');
 * ...
 * log.debug('something happened');
 * ```
 *
 * To disable debug and info logs in production, add this snippet to your root module:
 * ```
 * @NgModule({
 *  imports: [
 *    LoggerModule.forRoot({ production: environment.production }),
 *    ...
 *  ]
 * })
 * export class AppModule {}
 *
 * If you want to process logs through other outputs than console, you can add LogOutput functions to Logger.outputs.
 */

/**
 * The possible log levels.
 * LogLevel.Off is never emitted and only used with Logger.level property to disable logs.
 */
export enum LogLevel {
  Off = 0,
  Error,
  Warning,
  Info,
  Debug,
}

/**
 * Log output handler function.
 */
export type LogOutput = (
  source: string,
  level: LogLevel,
  ...objects: any[]
) => void;

export class Logger {
  /**
   * Current logging level.
   * Set it to LogLevel.Off to disable logs completely.
   */
  static level = LogLevel.Debug;

  /**
   * Enables production mode.
   * Sets logging level to LogLevel.Warning.
   */
  static enableProductionMode() {
    Logger.level = LogLevel.Warning;
  }

  constructor(private source?: string) {}

  /**
   * Logs messages or objects with the debug level.
   * Works the same as console.log().
   */
  debug(...objects: any[]) {
    this.log(console.log, LogLevel.Debug, objects);
  }

  /**
   * Logs messages or objects with the error level.
   * Works the same as console.log().
   */
  error(...objects: any[]) {
    this.log(console.error, LogLevel.Error, objects);
  }

  /**
   * Logs messages or objects with the info level.
   * Works the same as console.log().
   */
  info(...objects: any[]) {
    this.log(console.info, LogLevel.Info, objects);
  }

  /**
   * Starts a timer with the given label. Outputs at the debug level.
   * @param objects The label of the timer
   */
  time(...objects: any[]) {
    this.log(console.time, LogLevel.Debug, objects);
  }

  /**
   * Ends the timer with the given label. Outputs at the debug level.
   * @param objects The label of the timer
   */
  timeEnd(...objects: any[]) {
    this.log(console.timeEnd, LogLevel.Debug, objects);
  }

  /**
   * Logs messages or objects with the warning level.
   * Works the same as console.log().
   */
  warn(...objects: any[]) {
    this.log(console.warn, LogLevel.Warning, objects);
  }

  private log(func: Function, level: LogLevel, objects: any[]) {
    if (level <= Logger.level) {
      const messageContent = objects.join(', ');
      const logMessage = this.source
        ? `[${this.source}] ${messageContent}`
        : messageContent;
      func.call(console, logMessage);
    }
  }
}
