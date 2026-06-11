// Mock IntersectionObserver for jsdom environment - must run before any test files
class MockIntersectionObserver implements IntersectionObserver {
    readonly root: Element | null = null;
    readonly rootMargin: string = '';
    readonly thresholds: ReadonlyArray<number> = [];

    constructor(_options?: IntersectionObserverInit) {}

    observe(_target: Element): void {}
    unobserve(_target: Element): void {}
    disconnect(): void {}
    takeRecords(): IntersectionObserverEntry[] {
        return [];
    }
}

(global as any).IntersectionObserver = MockIntersectionObserver;
