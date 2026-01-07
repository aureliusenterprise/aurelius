import { ComponentFixture, TestBed } from "@angular/core/testing";
import { EntitiesService } from "aurelius-data-access";
import { EntityService } from "../services/entity.service";
import { SEARCH_SERVICE_DEBOUNCE_MS, SearchService } from "../services/search.service";
import { Search } from "./search.component";

describe("SearchResults", () => {
    let fixture: ComponentFixture<Search>;

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

        fixture = TestBed.createComponent(Search);

        searchService = TestBed.inject(SearchService);
    });

    it("should create", () => {
        const component = fixture.componentInstance;
        expect(component).toBeTruthy();
    });

    it("should update input value when searchService query changes", async () => {
        const compiled = fixture.nativeElement as HTMLElement;
        const query = "test query";

        searchService.query.set(query);
        await fixture.whenStable();

        const searchInput = compiled.querySelector("#search-input") as HTMLInputElement;
        expect(searchInput.value).toBe(query);
    });
});
