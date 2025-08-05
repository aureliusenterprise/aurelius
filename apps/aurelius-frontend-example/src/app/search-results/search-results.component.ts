import { CommonModule } from "@angular/common";
import { ChangeDetectionStrategy, Component, inject } from "@angular/core";
import { FontAwesomeModule } from "@fortawesome/angular-fontawesome";
import { faEdit } from "@fortawesome/free-solid-svg-icons";
import { EntitiesService } from "aurelius-data-access";
import { Card } from "aurelius-ui";
import { EntityService } from "../services/entity.service";
import { SearchService } from "../services/search.service";

@Component({
    imports: [Card, CommonModule, FontAwesomeModule],
    selector: "aurelius-frontend-example-search-results",
    templateUrl: "./search-results.component.html",
    styleUrl: "./search-results.component.scss",
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SearchResults {
    /**
     * The entities service is used to perform CRUD operations on entities.
     */
    protected readonly entitiesService = inject(EntitiesService);

    /**
     * The entity service is used to control the current entity being edited.
     */
    protected readonly entityService = inject(EntityService);

    /**
     * The search service is used to access the current search results.
     */
    protected readonly searchService = inject(SearchService);

    /**
     * FontAwesome icons used in the component.
     */
    protected readonly faEdit = faEdit;

    /**
     * This is used to display the correct pluralization in the UI.
     */
    protected readonly pluralMap = { "=1": "# entity.", other: "# entities." };
}
