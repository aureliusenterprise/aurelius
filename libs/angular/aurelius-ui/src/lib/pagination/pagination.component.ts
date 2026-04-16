import { CommonModule } from "@angular/common";
import { ChangeDetectionStrategy, Component, computed, ContentChild, input, model, TemplateRef } from "@angular/core";

@Component({
    selector: "aurelius-ui-pagination",
    imports: [CommonModule],
    templateUrl: "./pagination.component.html",
    styleUrls: ["./pagination.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Pagination<T extends object> {
    /**
     * The template used to render the items on the current page.
     * The context of the template will have an `$implicit` property which contains the items for the current page.
     */
    @ContentChild(TemplateRef) readonly itemsTemplate?: TemplateRef<{ $implicit: T[] }>;

    /**
     * The list of items to paginate.
     */
    readonly items = input([] as T[]);

    /**
     * The number of items to display per page.
     */
    readonly pageSize = input(10);

    /**
     * The index of the current page (0-based).
     */
    readonly pageIndex = model(0);

    /**
     * The items to display on the current page.
     */
    readonly page = computed(() => {
        const start = this.pageIndex() * this.pageSize();
        const end = start + this.pageSize();
        return this.items().slice(start, end);
    });

    /**
     * The total number of pages based on the length of the items and the page size.
     */
    readonly totalPages = computed(() => {
        return Math.ceil(this.items().length / this.pageSize());
    });

    /**
     * The current page number (1-based) for display purposes.
     */
    readonly currentPageDisplay = computed(() => {
        const totalPages = this.totalPages();
        if (totalPages === 0) {
            return 0;
        }
        return Math.min(this.pageIndex() + 1, totalPages);
    });

    /**
     * An array of page tokens to display in the pagination controls.
     * This includes page numbers and ellipses for skipped pages.
     */
    readonly pageTokens = computed(() => {
        return this.totalPages() <= 7 ? this.generateShortFormPageTokens() : this.generateLongFormPageTokens();
    });

    /**
     * Whether there is a previous page available.
     */
    readonly hasPreviousPage = computed(() => {
        return this.pageIndex() > 0;
    });

    /**
     * Whether there is a next page available.
     */
    readonly hasNextPage = computed(() => {
        return this.pageIndex() < this.totalPages() - 1;
    });

    /**
     * Navigate to a specific page by its index (0-based).
     * @param index The index of the page to navigate to.
     */
    goToPage(index: number) {
        if (index < 0 || index >= this.totalPages()) {
            return;
        }
        this.pageIndex.set(index);
    }

    /**
     * Navigate to the next page.
     */
    nextPage() {
        this.goToPage(this.pageIndex() + 1);
    }

    /**
     * Navigate to the previous page.
     */
    previousPage() {
        this.goToPage(this.pageIndex() - 1);
    }

    /**
     * Generate page tokens for the pagination controls when the total number of pages is small.
     */
    private generateShortFormPageTokens(): Array<number> {
        return Array.from({ length: this.totalPages() }, (_, index) => index + 1);
    }

    /**
     * Generate page tokens for the pagination controls when the total number of pages is large, including ellipses for skipped pages.
     */
    private generateLongFormPageTokens(): Array<number | "ellipsis"> {
        const totalPages = this.totalPages();
        const currentPage = this.currentPageDisplay();

        // Always include the first page
        const tokens: Array<number | "ellipsis"> = [1];

        // Determine the range of page numbers to display around the current page
        const middleStart = Math.max(2, currentPage - 1);
        const middleEnd = Math.min(totalPages - 1, currentPage + 1);

        // Add an ellipsis if there is a gap between the first page and the start of the middle range
        if (middleStart > 2) {
            tokens.push("ellipsis");
        }

        // Add the page numbers in the middle range
        for (let page = middleStart; page <= middleEnd; page += 1) {
            tokens.push(page);
        }

        // Add an ellipsis if there is a gap between the end of the middle range and the last page
        if (middleEnd < totalPages - 1) {
            tokens.push("ellipsis");
        }

        // Always include the last page
        tokens.push(totalPages);

        return tokens;
    }
}
