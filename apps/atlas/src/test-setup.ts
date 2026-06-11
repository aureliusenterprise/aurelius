import 'zone.js';
import 'jest-preset-angular/setup-jest';

// Mock IntersectionObserver for Jest environment
class MockIntersectionObserver {
    observe = () => {};
    disconnect = () => {};
    unobserve = () => {};
}
Object.defineProperty(window, 'IntersectionObserver', {
    value: MockIntersectionObserver,
    writable: true,
    configurable: true,
});
