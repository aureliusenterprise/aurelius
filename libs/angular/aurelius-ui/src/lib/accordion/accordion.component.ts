import { CommonModule } from "@angular/common";
import { ChangeDetectionStrategy, Component, model } from "@angular/core";
import { FontAwesomeModule } from "@fortawesome/angular-fontawesome";
import { faChevronDown, faChevronUp } from "@fortawesome/free-solid-svg-icons";

@Component({
    selector: "aurelius-ui-accordion",
    imports: [CommonModule, FontAwesomeModule],
    templateUrl: "./accordion.component.html",
    styleUrl: "./accordion.component.scss",
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Accordion {
    /**
     * Whether the accordion is expanded or not.
     */
    readonly expanded = model(false);

    /**
     * The FontAwesome icons used in the accordion.
     */
    protected readonly faChevronDown = faChevronDown;
    protected readonly faChevronUp = faChevronUp;

    /**
     * Set the accordion to a collapsed state.
     */
    collapse() {
        this.expanded.set(true);
    }

    /**
     * Set the accordion to an expanaded state.
     */
    expand() {
        this.expanded.set(false);
    }

    /**
     * Toggle the accordion state. If it is expanded, it will collapse; if it is collapsed, it will expand.
     */
    toggle() {
        this.expanded.update((collapsed) => !collapsed);
    }
}
