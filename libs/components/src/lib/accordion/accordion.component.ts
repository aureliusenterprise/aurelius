import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { faChevronDown, faChevronUp } from '@fortawesome/free-solid-svg-icons';

/**
 * Accordion component that can be expanded or collapsed.
 */
@Component({
    selector: 'models4insight-accordion',
    templateUrl: 'accordion.component.html',
    styleUrls: ['accordion.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class AccordionComponent {
    /**
     * Whether the accordion is collapsed or not.
     */
    @Input() collapsed = true;

    /**
     * The FontAwesome icons used in the accordion.
     */
    protected readonly faChevronDown = faChevronDown;
    protected readonly faChevronUp = faChevronUp;

    /**
     * Set the accordion to a collapsed state.
     */
    collapse() {
        this.collapsed = true;
    }

    /**
     * Set the accordion to an expanaded state.
     */
    expand() {
        this.collapsed = false;
    }

    /**
     * Toggle the accordion state. If it is expanded, it will collapse; if it is collapsed, it will expand.
     */
    toggle() {
        this.collapsed = !this.collapsed;
    }
}
