/**
 * Logger Utility
 * Simple logging utility with different log levels
 */

export enum LogLevel {
    DEBUG = 0,
    INFO = 1,
    WARN = 2,
    ERROR = 3
}

interface LogEntry {
    level: LogLevel;
    message: string;
    timestamp: Date;
    data?: any;
}

class Logger {
    private logLevel: LogLevel = LogLevel.INFO;
    private logs: LogEntry[] = [];
    private maxLogs: number = 1000;

    constructor() {
        // Set log level based on environment
        if (import.meta.env.DEV) {
            this.logLevel = LogLevel.DEBUG;
        }
    }

    private log(level: LogLevel, message: string, data?: any): void {
        if (level < this.logLevel) return;

        const entry: LogEntry = {
            level,
            message,
            timestamp: new Date(),
            data
        };

        // Store log entry
        this.logs.push(entry);
        if (this.logs.length > this.maxLogs) {
            this.logs.shift();
        }

        // Output to console
        const prefix = `[${LogLevel[level]}] ${entry.timestamp.toISOString()}:`;
        
        switch (level) {
            case LogLevel.DEBUG:
                console.debug(prefix, message, data || '');
                break;
            case LogLevel.INFO:
                console.info(prefix, message, data || '');
                break;
            case LogLevel.WARN:
                console.warn(prefix, message, data || '');
                break;
            case LogLevel.ERROR:
                console.error(prefix, message, data || '');
                break;
        }
    }

    debug(message: string, data?: any): void {
        this.log(LogLevel.DEBUG, message, data);
    }

    info(message: string, data?: any): void {
        this.log(LogLevel.INFO, message, data);
    }

    warn(message: string, data?: any): void {
        this.log(LogLevel.WARN, message, data);
    }

    error(message: string, data?: any): void {
        this.log(LogLevel.ERROR, message, data);
    }

    lifecycle(event: string, message: string, data?: any): void {
        this.log(LogLevel.INFO, `[${event.toUpperCase()}] ${message}`, data);
    }

    webSocket(event: string, data?: any): void {
        this.log(LogLevel.DEBUG, `[WS-${event.toUpperCase()}] WebSocket ${event}`, data);
    }

    getLogs(): LogEntry[] {
        return [...this.logs];
    }

    clearLogs(): void {
        this.logs = [];
    }

    setLogLevel(level: LogLevel): void {
        this.logLevel = level;
    }

    getLogLevel(): LogLevel {
        return this.logLevel;
    }
}

// Export singleton instance
export const logger = new Logger();

// Export factory function for creating new logger instances
export const createLogger = (): Logger => new Logger();

// Export default for backward compatibility
export default logger;