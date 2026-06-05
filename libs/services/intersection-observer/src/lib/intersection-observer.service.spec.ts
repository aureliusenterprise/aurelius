import { TestBed } from '@angular/core/testing';
import { ElementRef } from '@angular/core';
import { of } from 'rxjs';

import { IntersectionObserverService } from './intersection-observer.service';
import { IntersectionObserverProvider } from './intersection-observer.service';

// Mock IntersectionObserver for jsdom environment
class MockIntersectionObserver implements IntersectionObserver {
    readonly root: Element | null = null;
    readonly rootMargin: string = '';
    readonly thresholds: ReadonlyArray<number> = [0];
    constructor(public callback: IntersectionObserverCallback) {}
    disconnect() {}
    observe(target: Element) {}
    takeRecords(): IntersectionObserverEntry[] {
        return [];
    }
    unobserve(target: Element) {}
}

if (typeof window !== 'undefined' && !(window as any).IntersectionObserver) {
    (window as any).IntersectionObserver = MockIntersectionObserver;
}

describe('IntersectionObserverService', () => {
    beforeEach(() =>
        TestBed.configureTestingModule({
            providers: [
                IntersectionObserverService,
                { provide: ElementRef, useValue: { nativeElement: document.createElement('div') } },
                {
                    provide: IntersectionObserverProvider,
                    useValue: {
                        observe: jest.fn(),
                        unobserve: jest.fn(),
                        disconnect: jest.fn(),
                        elementsIntersectionStateChanged: of(),
                    },
                },
            ],
            teardown: { destroyAfterEach: false },
        }),
    );

    it('should be created', () => {
        const service: IntersectionObserverService = TestBed.get(IntersectionObserverService);
        expect(service).toBeTruthy();
    });
});
