import { ComponentFixture, TestBed } from "@angular/core/testing";
import { ReactiveFormsModule } from "@angular/forms";
import { EntitiesService } from "aurelius-data-access";
import { of } from "rxjs";
import { beforeEach, describe, expect, it } from "vitest";
import { EntityService } from "../services/entity.service";
import { SEARCH_SERVICE_DEBOUNCE_MS, SearchService } from "../services/search.service";
import { Editor } from "./editor.component";

describe("Editor", () => {
    let component: Editor;
    let fixture: ComponentFixture<Editor>;

    let entityService: EntityService;
    let searchService: SearchService;
    let entitiesService: EntitiesService;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [ReactiveFormsModule],
            providers: [
                EntityService,
                SearchService,
                EntitiesService,
                { provide: SEARCH_SERVICE_DEBOUNCE_MS, useValue: 25 },
            ],
        }).compileComponents();

        fixture = TestBed.createComponent(Editor);
        component = fixture.componentInstance;

        entityService = TestBed.inject(EntityService);
        searchService = TestBed.inject(SearchService);
        entitiesService = TestBed.inject(EntitiesService);
    });

    it("should create", () => {
        expect(component).toBeTruthy();
    });

    it("should clear entity on cancel", () => {
        vi.spyOn(entityService, "clear").mockImplementationOnce(() => null);

        component.cancel();

        expect(entityService.clear).toHaveBeenCalled();
    });

    it("should delete entity and clear state", async () => {
        vi.spyOn(entitiesService, "delete").mockImplementationOnce(() => of(void 0));
        vi.spyOn(entityService, "clear").mockImplementationOnce(() => null);

        await component.delete("test-guid");

        expect(entitiesService.delete).toHaveBeenCalledWith("test-guid");
        expect(entityService.clear).toHaveBeenCalled();
    });

    it("should not call delete if guid is null", async () => {
        vi.spyOn(entitiesService, "delete").mockImplementationOnce(() => of(void 0));
        vi.spyOn(searchService, "refresh").mockImplementationOnce(() => null);
        vi.spyOn(entityService, "clear").mockImplementationOnce(() => null);

        await component.delete(null);

        expect(entitiesService.delete).not.toHaveBeenCalled();
        expect(entityService.clear).toHaveBeenCalled();
    });

    it("should save entity and clear state", async () => {
        const entity = { description: "desc", guid: "g", name: "n" };

        vi.spyOn(entitiesService, "createOrUpdate").mockImplementationOnce(() => of(entity));
        vi.spyOn(entityService, "clear").mockImplementationOnce(() => null);

        entityService.edit(entity);
        await fixture.whenStable();

        await component.save();

        expect(entitiesService.createOrUpdate).toHaveBeenCalledWith(entity);
        expect(entityService.clear).toHaveBeenCalled();
    });

    it("should patch form when updateEntityForm called with entity", async () => {
        const compiled = fixture.nativeElement as HTMLElement;

        const entity = { description: "d", guid: "g", name: "n" };
        entityService.edit(entity);
        await fixture.whenStable();

        expect(compiled.querySelector<HTMLInputElement>("#guid")?.value).toEqual(entity.guid);
        expect(compiled.querySelector<HTMLInputElement>("#name")?.value).toEqual(entity.name);
        expect(compiled.querySelector<HTMLInputElement>("#description")?.value).toEqual(entity.description);
    });

    it("should reset form when updateEntityForm called with null", async () => {
        const compiled = fixture.nativeElement as HTMLElement;

        const entity = { description: "d", guid: "g", name: "n" };
        entityService.edit(entity);
        await fixture.whenStable();

        expect(compiled.querySelector<HTMLInputElement>("#guid")?.value).toEqual(entity.guid);
        expect(compiled.querySelector<HTMLInputElement>("#name")?.value).toEqual(entity.name);
        expect(compiled.querySelector<HTMLInputElement>("#description")?.value).toEqual(entity.description);

        entityService.clear();
        await fixture.whenStable();

        expect(compiled.querySelector<HTMLInputElement>("input#guid")?.value).toBeUndefined();
        expect(compiled.querySelector<HTMLInputElement>("input#name")?.value).toBeUndefined();
        expect(compiled.querySelector<HTMLInputElement>("input#description")?.value).toBeUndefined();
    });
});
