import { Logger, LogLevel } from './logger';

const logMethods = ['log', 'info', 'warn', 'error'];

describe('Logger', () => {
    let savedConsole: Record<string, Function>;
    let savedLevel: LogLevel;

    beforeAll(() => {
        savedConsole = {};
        logMethods.forEach((m) => {
            savedConsole[m] = console[m];
            console[m] = () => {};
        });
        savedLevel = Logger.level;
    });

    afterEach(() => {
        jest.clearAllMocks();
        Logger.level = LogLevel.Debug;
    });

    afterAll(() => {
        logMethods.forEach((m) => {
            console[m] = savedConsole[m];
        });
        Logger.level = savedLevel;
    });

    it('should create an instance', () => {
        expect(new Logger()).toBeTruthy();
    });

    it('should log at debug level when level is Debug', () => {
        // Arrange
        const consoleLogSpy = jest.spyOn(console, 'log').mockImplementation(() => {});
        const log = new Logger('test');
        Logger.level = LogLevel.Debug;

        // Act
        log.debug('message');

        // Assert
        expect(consoleLogSpy).toHaveBeenCalledWith('[test] message');
    });

    it('should not log at debug level when level is Warning', () => {
        // Arrange
        const consoleLogSpy = jest.spyOn(console, 'log').mockImplementation(() => {});
        const log = new Logger('test');
        Logger.level = LogLevel.Warning;

        // Act
        log.debug('message');

        // Assert
        expect(consoleLogSpy).not.toHaveBeenCalled();
    });

    it('should log at warning level when level is Warning', () => {
        // Arrange
        const consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation(() => {});
        const log = new Logger('test');
        Logger.level = LogLevel.Warning;

        // Act
        log.warn('message');

        // Assert
        expect(consoleWarnSpy).toHaveBeenCalledWith('[test] message');
    });

    it('should log at error level when level is Error', () => {
        // Arrange
        const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
        const log = new Logger('test');
        Logger.level = LogLevel.Error;

        // Act
        log.error('message');

        // Assert
        expect(consoleErrorSpy).toHaveBeenCalledWith('[test] message');
    });

    it('should enable production mode', () => {
        // Arrange & Act
        Logger.enableProductionMode();

        // Assert
        expect(Logger.level).toBe(LogLevel.Warning);
    });

    it('should log without source when no source is provided', () => {
        // Arrange
        const consoleLogSpy = jest.spyOn(console, 'log').mockImplementation(() => {});
        const log = new Logger();
        Logger.level = LogLevel.Debug;

        // Act
        log.debug('message');

        // Assert
        expect(consoleLogSpy).toHaveBeenCalledWith('message');
    });
});
