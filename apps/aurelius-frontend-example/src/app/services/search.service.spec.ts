import { TestBed } from "@angular/core/testing";
import { EntitiesService, Entity, Envelope, PaginatedResponse } from "aurelius-data-access";
import { of, Subject, throwError } from "rxjs";
import { SEARCH_SERVICE_DEBOUNCE_MS, SearchService } from "./search.service";

describe("SearchService", () => {
    let service: SearchService;
    let entitiesService: EntitiesService;
    let entitiesSubject: Subject<Envelope<Entity>>;

    beforeEach(() => {
        entitiesSubject = new Subject<Envelope<Entity>>();
        TestBed.configureTestingModule({
            providers: [
                SearchService,
                { provide: EntitiesService, useValue: { findAll: vi.fn(), entities$: entitiesSubject } },
                { provide: SEARCH_SERVICE_DEBOUNCE_MS, useValue: 25 },
            ],
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
                const response: PaginatedResponse<Entity> = {
                    data: [{ guid: "1", name: "A", description: "desc" }],
                    total: 1,
                };

                vi.spyOn(entitiesService, "findAll").mockReturnValueOnce(of(response));

                service.refresh();

                setTimeout(() => {
                    expect(entitiesService.findAll).toHaveBeenCalledWith({
                        search: service.query(),
                        limit: service.pageSize(),
                        skip: service.pageIndex() * service.pageSize(),
                    });
                    expect(service.entities()).toEqual(response);
                    done();
                }, 100);
            }),
        200,
    );

    it(
        "should update query and trigger search",
        () =>
            new Promise<void>((done) => {
                const response: PaginatedResponse<Entity> = {
                    data: [{ guid: "2", name: "B", description: "desc2" }],
                    total: 1,
                };

                vi.spyOn(entitiesService, "findAll").mockReturnValueOnce(of(response));

                service.query.set("B");

                setTimeout(() => {
                    expect(entitiesService.findAll).toHaveBeenCalledWith({
                        search: service.query(),
                        limit: service.pageSize(),
                        skip: service.pageIndex() * service.pageSize(),
                    });
                    expect(service.entities()).toEqual(response);
                    done();
                }, 100);
            }),
        200,
    );

    it(
        "should update pageIndex and trigger search",
        () =>
            new Promise<void>((done) => {
                const response: PaginatedResponse<Entity> = {
                    data: [{ guid: "2", name: "B", description: "desc2" }],
                    total: 1,
                };

                vi.spyOn(entitiesService, "findAll").mockReturnValueOnce(of(response));

                service.pageIndex.set(1);

                setTimeout(() => {
                    expect(entitiesService.findAll).toHaveBeenCalledWith({
                        search: service.query(),
                        limit: service.pageSize(),
                        skip: service.pageIndex() * service.pageSize(),
                    });
                    expect(service.entities()).toEqual(response);
                    done();
                }, 100);
            }),
        200,
    );

    it(
        "should update pageSize and trigger search",
        () =>
            new Promise<void>((done) => {
                const response: PaginatedResponse<Entity> = {
                    data: [{ guid: "2", name: "B", description: "desc2" }],
                    total: 1,
                };

                vi.spyOn(entitiesService, "findAll").mockReturnValueOnce(of(response));

                service.pageSize.set(10);

                setTimeout(() => {
                    expect(entitiesService.findAll).toHaveBeenCalledWith({
                        search: service.query(),
                        limit: service.pageSize(),
                        skip: service.pageIndex() * service.pageSize(),
                    });
                    expect(service.entities()).toEqual(response);
                    done();
                }, 100);
            }),
        200,
    );

    it(
        "should debounce rapid queries",
        () =>
            new Promise<void>((done) => {
                const response: PaginatedResponse<Entity> = {
                    data: [{ guid: "3", name: "C", description: "desc3" }],
                    total: 1,
                };

                vi.spyOn(entitiesService, "findAll").mockReturnValue(of(response));

                service.query.set("C1");
                service.query.set("C2");
                service.query.set("C3");

                setTimeout(() => {
                    expect(entitiesService.findAll).toHaveBeenCalledTimes(1);
                    expect(service.entities()).toEqual(response);
                    done();
                }, 100);
            }),
        200,
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
                    expect(service.entities()).toEqual({ data: [], total: 0 });
                    done();
                }, 100);
            }),
        200,
    );

    it(
        "should trigger refresh when entities$ emits an event",
        () =>
            new Promise<void>((done) => {
                const refreshSpy = vi.spyOn(service, "refresh");

                // Simulate an entity update event from the server
                entitiesSubject.next({
                    guid: "4",
                    timestamp: new Date().toISOString(),
                    value: { guid: "4", name: "D", description: "desc4" },
                });

                setTimeout(() => {
                    expect(refreshSpy).toHaveBeenCalledOnce();
                    done();
                }, 100);
            }),
        200,
    );
});
