import { TestBed } from "@angular/core/testing";
import { EntitiesService, Entity, Envelope } from "aurelius-data-access";
import { Subject } from "rxjs";
import { EntityService } from "./entity.service";

describe("EntityService", () => {
    let service: EntityService;
    let entitiesSubject: Subject<Envelope<Entity>>;

    beforeEach(() => {
        entitiesSubject = new Subject<Envelope<Entity>>();

        TestBed.configureTestingModule({
            providers: [
                EntityService,
                { provide: EntitiesService, useValue: { entities$: entitiesSubject.asObservable() } },
            ],
        });
        service = TestBed.inject(EntityService);
    });

    afterEach(() => {
        entitiesSubject.complete();
    });

    it("should initialize with null entity", () => {
        expect(service.entity()).toBeNull();
    });

    it("should clear the entity", () => {
        service.entity.set({ guid: "123", name: "Test", description: "Desc" });
        service.clear();
        expect(service.entity()).toBeNull();
    });

    it("should create a new entity with default values", () => {
        service.create();
        expect(service.entity()).toEqual({ guid: undefined, name: "", description: "" });
    });

    it("should edit an existing entity", () => {
        const entity: Entity = { guid: "abc", name: "Name", description: "Desc" };
        service.edit(entity);
        expect(service.entity()).toEqual(entity);
    });

    it(
        "should update the current entity when receiving an update for the same GUID",
        () =>
            new Promise<void>((done) => {
                const initialEntity: Entity = { guid: "123", name: "Original", description: "Desc" };
                service.edit(initialEntity);

                const updatedEntity: Entity = { guid: "123", name: "Updated", description: "New Desc" };

                const envelope: Envelope<Entity> = {
                    guid: "123",
                    timestamp: new Date().toISOString(),
                    value: updatedEntity,
                };

                entitiesSubject.next(envelope);

                setTimeout(() => {
                    expect(service.entity()).toEqual(updatedEntity);
                    done();
                }, 50);
            }),
        100,
    );

    it(
        "should clear the entity when receiving a deletion (null value) for the current GUID",
        () =>
            new Promise<void>((done) => {
                const initialEntity: Entity = { guid: "123", name: "Original", description: "Desc" };
                service.edit(initialEntity);

                const deleteEnvelope: Envelope<Entity> = {
                    guid: "123",
                    timestamp: new Date().toISOString(),
                    value: null,
                };

                entitiesSubject.next(deleteEnvelope);

                setTimeout(() => {
                    expect(service.entity()).toBeNull();
                    done();
                }, 50);
            }),
        100,
    );

    it(
        "should NOT update the entity when receiving an update for a different GUID",
        () =>
            new Promise<void>((done) => {
                const currentEntity: Entity = { guid: "123", name: "Current", description: "Desc" };
                service.edit(currentEntity);

                // Simulate update for a different entity with different GUID
                const otherEntity: Entity = { guid: "456", name: "Other", description: "Other Desc" };

                const envelope: Envelope<Entity> = {
                    guid: "456",
                    timestamp: new Date().toISOString(),
                    value: otherEntity,
                };

                entitiesSubject.next(envelope);

                setTimeout(() => {
                    expect(service.entity()).toEqual(currentEntity);
                    done();
                }, 50);
            }),
        100,
    );

    it(
        "should NOT update the entity when receiving a deletion for a different GUID",
        () =>
            new Promise<void>((done) => {
                const currentEntity: Entity = { guid: "123", name: "Current", description: "Desc" };
                service.edit(currentEntity);

                // Simulate deletion of a different entity
                const deleteEnvelope: Envelope<Entity> = {
                    guid: "456",
                    timestamp: new Date().toISOString(),
                    value: null,
                };

                entitiesSubject.next(deleteEnvelope);

                setTimeout(() => {
                    expect(service.entity()).toEqual(currentEntity);
                    done();
                }, 50);
            }),
        100,
    );

    it(
        "should NOT update the entity when current is null and receives an update for a new GUID",
        () =>
            new Promise<void>((done) => {
                // Start with no current entity
                expect(service.entity()).toBeNull();

                const newEntity: Entity = { guid: "789", name: "New Entity", description: "First Desc" };

                const envelope: Envelope<Entity> = {
                    guid: "789",
                    timestamp: new Date().toISOString(),
                    value: newEntity,
                };

                entitiesSubject.next(envelope);

                setTimeout(() => {
                    expect(service.entity()).toBeNull();
                    done();
                }, 50);
            }),
        100,
    );
});
