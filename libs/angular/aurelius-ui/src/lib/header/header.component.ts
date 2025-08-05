import { CommonModule } from "@angular/common";
import { ChangeDetectionStrategy, Component, input, model } from "@angular/core";

@Component({
    selector: "aurelius-ui-header",
    imports: [CommonModule],
    templateUrl: "./header.component.html",
    styleUrl: "./header.component.scss",
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Header {
    /**
     * Whether the header menu is expanded or not.
     */
    readonly expanded = model(false);

    /**
     * The logo to display in the header.
     */
    readonly logo = input<string>();

    /**
     * The name of the application to display in the header.
     */
    readonly name = input<string>();

    /**
     * Close the header menu.
     */
    close(): void {
        this.expanded.set(false);
    }

    /**
     * Open the header menu.
     */
    open(): void {
        this.expanded.set(true);
    }

    /**
     * Open or close the header menu based on its current state.
     */
    toggle(): void {
        this.expanded.update((expanded) => !expanded);
    }
}
