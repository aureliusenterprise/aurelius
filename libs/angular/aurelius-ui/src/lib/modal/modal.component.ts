import { CommonModule } from "@angular/common";
import { ChangeDetectionStrategy, Component, input, model } from "@angular/core";

@Component({
    selector: "aurelius-ui-modal",
    imports: [CommonModule],
    templateUrl: "./modal.component.html",
    styleUrl: "./modal.component.scss",
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Modal {
    /**
     * Whether or not the modal is currently open.
     */
    readonly active = model(false);

    /**
     * Whether or not to show the close button.
     */
    readonly showCloseButton = input(true);

    /**
     * Close the modal.
     */
    close(): void {
        this.active.set(false);
    }

    /**
     * Open the modal.
     */
    open(): void {
        this.active.set(true);
    }

    /**
     * Open the modal if it is closed, or close it if it is open.
     */
    toggle(): void {
        this.active.update((active) => !active);
    }
}
