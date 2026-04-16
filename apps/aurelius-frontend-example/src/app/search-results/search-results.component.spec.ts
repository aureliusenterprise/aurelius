import { ComponentFixture, TestBed } from "@angular/core/testing";
import { EntitiesService, Entity } from "aurelius-data-access";
import { EntityService } from "../services/entity.service";
import { SEARCH_SERVICE_DEBOUNCE_MS, SearchService } from "../services/search.service";
import { SearchResults } from "./search-results.component";

describe("SearchResults", () => {
    let fixture: ComponentFixture<SearchResults>;

    let entityService: EntityService;
    let searchService: SearchService;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            providers: [
                EntityService,
                SearchService,
                EntitiesService,
                { provide: SEARCH_SERVICE_DEBOUNCE_MS, useValue: 25 },
            ],
        }).compileComponents();

        fixture = TestBed.createComponent(SearchResults);

        entityService = TestBed.inject(EntityService);
        searchService = TestBed.inject(SearchService);
    });

    it("should render a card for each entity", async () => {
        const entities = [
            { guid: "1", name: "Entity One" },
            { guid: "2", name: "Entity Two" },
        ] as Entity[];

        vi.spyOn(searchService, "entities").mockImplementationOnce(() => ({ data: entities, total: entities.length }));

        await fixture.whenStable();

        const compiled = fixture.nativeElement as HTMLElement;

        for (const entity of entities) {
            expect(compiled.querySelector(`aurelius-ui-card[data-guid="${entity.guid}"]`)).not.toBeNull();
        }
    });

    it("should not render the results section if there are no entities", async () => {
        vi.spyOn(searchService, "entities").mockImplementationOnce(() => ({ data: [], total: 0 }));

        await fixture.whenStable();

        const compiled = fixture.nativeElement as HTMLElement;
        const resultsSection = compiled.querySelector("section");

        expect(resultsSection).toBeNull();
    });

    it("should call entityService.edit when edit button is clicked", async () => {
        const entity = { guid: "1", name: "Entity One" } as Entity;

        vi.spyOn(searchService, "entities").mockImplementationOnce(() => ({ data: [entity], total: 1 }));

        const editSpy = vi.spyOn(entityService, "edit").mockImplementationOnce(() => null);

        await fixture.whenStable();

        const compiled = fixture.nativeElement as HTMLElement;
        const editButton = compiled.querySelector(`#edit-entity-${entity.guid}`) as HTMLButtonElement;

        editButton.click();

        expect(editSpy).toHaveBeenCalledWith(entity);
    });
});
