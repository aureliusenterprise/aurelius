import { HttpTestingController, provideHttpClientTesting } from "@angular/common/http/testing";
import { TestBed } from "@angular/core/testing";
import { EntitiesService, Entity, FindAllQueryParams } from "./entities.service";

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

    afterEach(() => {
        httpMock.verify();
    });

    it("should be created", () => {
        expect(service).toBeTruthy();
    });

    it("should create or update an entity", () => {
        const entity: Entity = { name: "Test", description: "Desc" };
        const response: Entity = { guid: "123", ...entity };

        service.createOrUpdate(entity).subscribe((result) => {
            expect(result).toEqual(response);
        });

        const req = httpMock.expectOne("/api/entities/");

        expect(req.request.method).toBe("PUT");
        expect(req.request.body).toEqual(entity);

        req.flush(response);
    });

    it("should delete an entity by guid", () => {
        const guid = "abc-123";

        service.delete(guid).subscribe((result) => {
            expect(result).toBeNull();
        });

        const req = httpMock.expectOne(`/api/entities/${guid}`);

        expect(req.request.method).toBe("DELETE");

        req.flush(null);
    });

    it("should fetch all entities", () => {
        const params: FindAllQueryParams = { limit: 10, search: "foo", skip: 2 };
        const entities: Entity[] = [
            { guid: "1", name: "A", description: "desc A" },
            { guid: "2", name: "B", description: "desc B" },
        ];

        service.findAll(params).subscribe((result) => {
            expect(result).toEqual(entities);
        });

        const req = httpMock.expectOne((r) => r.url === "/api/entities/");

        expect(req.request.method).toBe("GET");
        expect(req.request.params.get("limit")).toBe("10");
        expect(req.request.params.get("search")).toBe("foo");
        expect(req.request.params.get("skip")).toBe("2");

        req.flush(entities);
    });

    it("should fetch a specific entity by guid", () => {
        const guid = "xyz-789";
        const entity: Entity = { guid, name: "C", description: "desc C" };

        service.findOne(guid).subscribe((result) => {
            expect(result).toEqual(entity);
        });

        const req = httpMock.expectOne(`/api/entities/${guid}`);

        expect(req.request.method).toBe("GET");

        req.flush(entity);
    });
});
