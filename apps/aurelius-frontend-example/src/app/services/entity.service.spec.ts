import { TestBed } from "@angular/core/testing";
import { Entity } from "aurelius-data-access";
import { EntityService } from "./entity.service";

describe("EntityService", () => {
    let service: EntityService;

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [EntityService],
        });
        service = TestBed.inject(EntityService);
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
});
