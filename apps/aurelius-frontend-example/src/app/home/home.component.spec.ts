import { ComponentFixture, TestBed } from "@angular/core/testing";
import { Home } from "./home.component";
import { Editor } from "../editor/editor.component";
import { Search } from "../search/search.component";
import { SearchResults } from "../search-results/search-results.component";
import { CommonModule } from "@angular/common";

describe("Home", () => {
    let fixture: ComponentFixture<Home>;
    let component: Home;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [CommonModule, Home, Editor, Search, SearchResults],
        }).compileComponents();

        fixture = TestBed.createComponent(Home);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it("should create", () => {
        expect(component).toBeTruthy();
    });

    it("should render the editor, search, and search-results components", () => {
        const compiled = fixture.nativeElement as HTMLElement;
        expect(compiled.querySelector("aurelius-frontend-example-editor")).toBeTruthy();
        expect(compiled.querySelector("aurelius-frontend-example-search")).toBeTruthy();
        expect(compiled.querySelector("aurelius-frontend-example-search-results")).toBeTruthy();
    });
});
