import { TestBed } from "@angular/core/testing";
import { EntitiesService, Entity } from "aurelius-data-access";
import { of, throwError } from "rxjs";
import { SearchService, SEARCH_SERVICE_DEBOUNCE_MS } from "./search.service";

describe("SearchService", () => {
    let service: SearchService;
    let entitiesService: EntitiesService;

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [SearchService, EntitiesService, { provide: SEARCH_SERVICE_DEBOUNCE_MS, useValue: 25 }],
        });
        service = TestBed.inject(SearchService);
        entitiesService = TestBed.inject(EntitiesService);
    });

    it("should be created", () => {
        expect(service).toBeTruthy();
    });

    it(
        "should trigger refresh and call findAll",
        () =>
            new Promise<void>((done) => {
                const entities: Entity[] = [{ guid: "1", name: "A", description: "desc" }];

                vi.spyOn(entitiesService, "findAll").mockReturnValueOnce(of(entities));

                service.refresh();

                setTimeout(() => {
                    expect(service.entities()).toEqual(entities);
                    done();
                }, 50);
            }),
        100,
    );

    it(
        "should update query and trigger search",
        () =>
            new Promise<void>((done) => {
                const entities: Entity[] = [{ guid: "2", name: "B", description: "desc2" }];

                vi.spyOn(entitiesService, "findAll").mockReturnValueOnce(of(entities));

                service.query.set("B");

                setTimeout(() => {
                    expect(entitiesService.findAll).toHaveBeenCalledWith({ search: "B" });
                    expect(service.entities()).toEqual(entities);
                    done();
                }, 50);
            }),
        100,
    );

    it(
        "should debounce rapid queries",
        () =>
            new Promise<void>((done) => {
                const entities: Entity[] = [{ guid: "3", name: "C", description: "desc3" }];

                vi.spyOn(entitiesService, "findAll").mockReturnValue(of(entities));

                service.query.set("C1");
                service.query.set("C2");
                service.query.set("C3");

                setTimeout(() => {
                    expect(entitiesService.findAll).toHaveBeenCalledTimes(1);
                    expect(service.entities()).toEqual(entities);
                    done();
                }, 50);
            }),
        100,
    );

    it(
        "should handle error from findAll",
        () =>
            new Promise<void>((done) => {
                const err = new Error("fail");

                vi.spyOn(entitiesService, "findAll").mockReturnValueOnce(throwError(() => err));

                service.refresh();

                setTimeout(() => {
                    expect(service.error()).toBe(err);
                    expect(service.entities()).toEqual([]);
                    done();
                }, 50);
            }),
        100,
    );
});
