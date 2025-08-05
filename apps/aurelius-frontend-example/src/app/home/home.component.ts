import { CommonModule } from "@angular/common";
import { ChangeDetectionStrategy, Component } from "@angular/core";
import { Editor } from "../editor/editor.component";
import { SearchResults } from "../search-results/search-results.component";
import { Search } from "../search/search.component";

@Component({
    imports: [CommonModule, Editor, Search, SearchResults],
    selector: "aurelius-frontend-example-home",
    templateUrl: "./home.component.html",
    styleUrl: "./home.component.scss",
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Home {}
