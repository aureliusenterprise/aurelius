import { CommonModule } from "@angular/common";
import { ChangeDetectionStrategy, Component, inject } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { FontAwesomeModule } from "@fortawesome/angular-fontawesome";
import { faPlus, faSearch, faSync } from "@fortawesome/free-solid-svg-icons";
import { EntityService } from "../services/entity.service";
import { SearchService } from "../services/search.service";

@Component({
    imports: [CommonModule, FontAwesomeModule, FormsModule],
    selector: "aurelius-frontend-example-search",
    templateUrl: "./search.component.html",
    styleUrl: "./search.component.scss",
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Search {
    /**
     * The entity service is used to control the current entity being edited.
     */
    protected readonly entityService = inject(EntityService);

    /**
     * The search service is used to set the current query.
     */
    protected readonly searchService = inject(SearchService);

    /**
     * FontAwesome icons used in the component.
     */
    protected readonly faPlus = faPlus;
    protected readonly faSearch = faSearch;
    protected readonly faSync = faSync;
}
