import { TestBed } from "@angular/core/testing";
import { API_BASE_URL, provideApiBaseUrl } from "./api-config";

describe("API_BASE_URL", () => {
    it("defaults to /api when not provided", () => {
        TestBed.configureTestingModule({});
        expect(TestBed.inject(API_BASE_URL)).toBe("/api");
    });

    it("uses the value from provideApiBaseUrl", () => {
        TestBed.configureTestingModule({ providers: [provideApiBaseUrl("https://api.example.com")] });
        expect(TestBed.inject(API_BASE_URL)).toBe("https://api.example.com");
    });
});
