import { HttpTestingController, provideHttpClientTesting } from "@angular/common/http/testing";
import { TestBed } from "@angular/core/testing";
import { EntitiesService, Entity, FindAllQueryParams, PaginatedResponse } from "./entities.service";

describe("EntitiesService", () => {
    let service: EntitiesService;
    let httpMock: HttpTestingController;

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [EntitiesService, provideHttpClientTesting()],
        });
        service = TestBed.inject(EntitiesService);
        httpMock = TestBed.inject(HttpTestingController);
    });

    it("should be created", () => {
        expect(service).toBeTruthy();
    });

    it("should create or update an entity", () =>
        new Promise<void>((done, fail) => {
            const entity: Entity = { name: "Test", description: "Desc" };
            const response: Entity = { guid: "123", ...entity };

            service.createOrUpdate(entity).subscribe({
                next: (result) => {
                    expect(result).toEqual(response);
                    done();
                },
                error: fail,
            });

            const req = httpMock.expectOne("/api/entities/");

            expect(req.request.method).toBe("PUT");
            expect(req.request.body).toEqual(entity);

            req.flush(response);
        }));

    it("should delete an entity by guid", () =>
        new Promise<void>((done, fail) => {
            const guid = "abc-123";

            service.delete(guid).subscribe({
                next: (result) => {
                    expect(result).toBeNull();
                    done();
                },
                error: fail,
            });

            const req = httpMock.expectOne(`/api/entities/${guid}`);

            expect(req.request.method).toBe("DELETE");

            req.flush(null);
        }));

    it("should fetch all entities", () =>
        new Promise<void>((done, fail) => {
            const params: FindAllQueryParams = { limit: 10, search: "foo", skip: 2 };

            const entities: Entity[] = [
                { guid: "1", name: "A", description: "desc A" },
                { guid: "2", name: "B", description: "desc B" },
            ];

            const paginatedResponse: PaginatedResponse<Entity> = { total: entities.length, data: entities };

            service.findAll(params).subscribe({
                next: (result) => {
                    expect(result).toEqual(paginatedResponse);
                    done();
                },
                error: fail,
            });

            const req = httpMock.expectOne((r) => r.url === "/api/entities/");

            expect(req.request.method).toBe("GET");
            expect(req.request.params.get("limit")).toBe("10");
            expect(req.request.params.get("search")).toBe("foo");
            expect(req.request.params.get("skip")).toBe("2");

            req.flush(paginatedResponse);
        }));

    it("should filter out undefined values from params", () =>
        new Promise<void>((done, fail) => {
            const params: FindAllQueryParams = { limit: 10, search: undefined, skip: 2 };

            const entities: Entity[] = [{ guid: "1", name: "A", description: "desc A" }];
            const paginatedResponse: PaginatedResponse<Entity> = { total: entities.length, data: entities };

            service.findAll(params).subscribe({
                next: (result) => {
                    expect(result).toEqual(paginatedResponse);
                    done();
                },
                error: fail,
            });

            const req = httpMock.expectOne((r) => r.url === "/api/entities/");

            expect(req.request.method).toBe("GET");
            expect(req.request.params.get("limit")).toBe("10");
            expect(req.request.params.has("search")).toBeFalsy();
            expect(req.request.params.get("skip")).toBe("2");

            req.flush(paginatedResponse);
        }));

    it("should filter out empty string values from params", () =>
        new Promise<void>((done, fail) => {
            const params: FindAllQueryParams = { limit: 10, search: "", skip: 2 };

            const entities: Entity[] = [{ guid: "1", name: "A", description: "desc A" }];
            const paginatedResponse: PaginatedResponse<Entity> = { total: entities.length, data: entities };

            service.findAll(params).subscribe({
                next: (result) => {
                    expect(result).toEqual(paginatedResponse);
                    done();
                },
                error: fail,
            });

            const req = httpMock.expectOne((r) => r.url === "/api/entities/");

            expect(req.request.method).toBe("GET");
            expect(req.request.params.get("limit")).toBe("10");
            expect(req.request.params.has("search")).toBeFalsy();
            expect(req.request.params.get("skip")).toBe("2");

            req.flush(paginatedResponse);
        }));

    it("should filter out 0 values from params", () =>
        new Promise<void>((done, fail) => {
            const params: FindAllQueryParams = { limit: 0, search: "foo", skip: 0 };

            const entities: Entity[] = [{ guid: "1", name: "A", description: "desc A" }];
            const paginatedResponse: PaginatedResponse<Entity> = { total: entities.length, data: entities };

            service.findAll(params).subscribe({
                next: (result) => {
                    expect(result).toEqual(paginatedResponse);
                    done();
                },
                error: fail,
            });

            const req = httpMock.expectOne((r) => r.url === "/api/entities/");

            expect(req.request.method).toBe("GET");
            expect(req.request.params.has("limit")).toBeFalsy();
            expect(req.request.params.get("search")).toBe("foo");
            expect(req.request.params.has("skip")).toBeFalsy();

            req.flush(paginatedResponse);
        }));

    it("should preserve non-zero positive numbers in params", () =>
        new Promise<void>((done, fail) => {
            const params: FindAllQueryParams = { limit: 10, search: "foo", skip: 2 };

            const entities: Entity[] = [{ guid: "1", name: "A", description: "desc A" }];
            const paginatedResponse: PaginatedResponse<Entity> = { total: entities.length, data: entities };

            service.findAll(params).subscribe({
                next: (result) => {
                    expect(result).toEqual(paginatedResponse);
                    done();
                },
                error: fail,
            });

            const req = httpMock.expectOne((r) => r.url === "/api/entities/");

            expect(req.request.method).toBe("GET");
            expect(req.request.params.get("limit")).toBe("10");
            expect(req.request.params.get("search")).toBe("foo");
            expect(req.request.params.get("skip")).toBe("2");

            req.flush(paginatedResponse);
        }));

    it("should preserve non-zero negative numbers in params", () =>
        new Promise<void>((done, fail) => {
            const params: FindAllQueryParams & { offset: number } = { limit: 10, offset: -5 };

            const entities: Entity[] = [{ guid: "1", name: "A", description: "desc A" }];
            const paginatedResponse: PaginatedResponse<Entity> = { total: entities.length, data: entities };

            service.findAll(params as FindAllQueryParams).subscribe({
                next: (result) => {
                    expect(result).toEqual(paginatedResponse);
                    done();
                },
                error: fail,
            });

            const req = httpMock.expectOne((r) => r.url === "/api/entities/");

            expect(req.request.method).toBe("GET");
            expect(req.request.params.get("limit")).toBe("10");
            expect(req.request.params.get("offset")).toBe("-5");

            req.flush(paginatedResponse);
        }));

    it("should preserve non-empty strings in params", () =>
        new Promise<void>((done, fail) => {
            const params: FindAllQueryParams = { limit: 10, search: "test query", skip: 0 };

            const entities: Entity[] = [{ guid: "1", name: "A", description: "desc A" }];
            const paginatedResponse: PaginatedResponse<Entity> = { total: entities.length, data: entities };

            service.findAll(params).subscribe({
                next: (result) => {
                    expect(result).toEqual(paginatedResponse);
                    done();
                },
                error: fail,
            });

            const req = httpMock.expectOne((r) => r.url === "/api/entities/");

            expect(req.request.method).toBe("GET");
            expect(req.request.params.get("limit")).toBe("10");
            expect(req.request.params.get("search")).toBe("test query");
            expect(req.request.params.has("skip")).toBeFalsy();

            req.flush(paginatedResponse);
        }));

    it("should fetch a specific entity by guid", () =>
        new Promise<void>((done, fail) => {
            const guid = "xyz-789";
            const entity: Entity = { guid, name: "C", description: "desc C" };

            service.findOne(guid).subscribe({
                next: (result) => {
                    expect(result).toEqual(entity);
                    done();
                },
                error: fail,
            });

            const req = httpMock.expectOne(`/api/entities/${guid}`);

            expect(req.request.method).toBe("GET");

            req.flush(entity);
        }));

    it("should receive entity updates", () =>
        new Promise<void>((done, fail) => {
            const envelope = { guid: "123", value: { guid: "123", name: "Updated", description: "Updated desc" } };

            service.entities$.subscribe({
                next: (notification) => {
                    expect(notification).toEqual(envelope);
                    done();
                },
                error: fail,
            });

            const req = httpMock.expectOne("/api/entities/sse");

            expect(req.request.method).toBe("GET");

            req.flush(`data: ${JSON.stringify(envelope)}\nevent: entity\n\n`, {
                headers: { "Content-Type": "text/event-stream" },
            });
        }));

    it("should filter notifications not related to entities", () =>
        new Promise<void>((done, fail) => {
            const envelope = { guid: "123", value: { guid: "123", name: "Updated", description: "Updated desc" } };

            service.entities$.subscribe({
                next: fail,
                error: fail,
            });

            const req = httpMock.expectOne("/api/entities/sse");

            expect(req.request.method).toBe("GET");

            req.flush(`data: ${JSON.stringify(envelope)}\nevent: test\n\n`, {
                headers: { "Content-Type": "text/event-stream" },
            });

            setTimeout(done, 200);
        }));

    it("should handle null data gracefully", () =>
        new Promise<void>((done, fail) => {
            service.entities$.subscribe({
                next: fail,
                error: fail,
            });

            const req = httpMock.expectOne("/api/entities/sse");

            expect(req.request.method).toBe("GET");

            req.flush("data: \nevent: entity\n\n", {
                headers: { "Content-Type": "text/event-stream" },
            });

            setTimeout(done, 200);
        }));
});
