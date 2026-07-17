import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { faChevronDown, faChevronUp } from '@fortawesome/free-solid-svg-icons';

/**
 * Accordion component that can be expanded or collapsed.
 */
@Component({
    selector: 'models4insight-accordion',
    templateUrl: 'accordion.component.html',
    styleUrls: ['accordion.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AccordionComponent {
    /**
     * Whether the accordion is expanded or not.
     */
    @Input() expanded = false;

    /**
     * The aria-label for the toggle button. Supports translation keys.
     */
    @Input() ariaLabel = 'components.accordion.toggleContent';

    /**
     * The FontAwesome icons used in the accordion.
     */
    protected readonly faChevronDown = faChevronDown;
    protected readonly faChevronUp = faChevronUp;

    /**
     * Set the accordion to a collapsed state.
     */
    collapse() {
        this.expanded = false;
    }

    /**
     * Set the accordion to an expanaded state.
     */
    expand() {
        this.expanded = true;
    }

    /**
     * Toggle the accordion state. If it is expanded, it will collapse; if it is collapsed, it will expand.
     */
    toggle() {
        this.expanded = !this.expanded;
    }
}
