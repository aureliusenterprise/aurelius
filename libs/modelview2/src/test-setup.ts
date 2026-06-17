import 'zone.js';
import 'jest-preset-angular/setup-jest';

// Mock IntersectionObserver for jsdom environment
class IntersectionObserverMock {
    root = null;
    rootMargin = '';
    thresholds = [];
    observe = jest.fn();
    unobserve = jest.fn();
    disconnect = jest.fn();
    takeRecords = jest.fn(() => []);
}

(global as any).IntersectionObserver = IntersectionObserverMock;
