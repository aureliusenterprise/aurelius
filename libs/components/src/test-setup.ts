import 'zone.js';
import 'jest-preset-angular/setup-jest';

// Mock IntersectionObserver for jsdom environment
if (!window.IntersectionObserver) {
    window.IntersectionObserver = class {
        readonly root: Element | null = null;
        readonly rootMargin: string = '';
        readonly thresholds: ReadonlyArray<number> = [];
        constructor(options?: IntersectionObserverInit, callback?: IntersectionObserverCallback) {}
        disconnect() {}
        observe(target: Element) {}
        takeRecords(): IntersectionObserverEntry[] {
            return [];
        }
        unobserve(target: Element) {}
    } as unknown as typeof IntersectionObserver;
}
