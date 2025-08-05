import { CommonModule } from "@angular/common";
import { ChangeDetectionStrategy, Component, effect, inject } from "@angular/core";
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from "@angular/forms";
import { EntitiesService, Entity } from "aurelius-data-access";
import { Modal } from "aurelius-ui";
import { firstValueFrom } from "rxjs";
import { EntityService } from "../services/entity.service";
import { SearchService } from "../services/search.service";

@Component({
    imports: [CommonModule, Modal, ReactiveFormsModule],
    selector: "aurelius-frontend-example-editor",
    templateUrl: "./editor.component.html",
    styleUrl: "./editor.component.scss",
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Editor {
    /**
     * The entity service is used to access the current entity being edited.
     */
    protected readonly entityService = inject(EntityService);

    /**
     * The form group for the entity being edited.
     */
    protected readonly entityForm = new FormGroup({
        description: new FormControl<string | null>(null, [Validators.maxLength(255)]),
        guid: new FormControl<string | null>(null),
        name: new FormControl<string | null>(null, [Validators.maxLength(100)]),
    });

    /**
     * The entities service is used to perform CRUD operations on entities.
     */
    private readonly entitiesService = inject(EntitiesService);

    /**
     * The search service is used to access the current search results.
     */
    private readonly searchService = inject(SearchService);

    /**
     * Initializes the editor component and sets up an effect to update the entity form
     * whenever the current entity changes.
     */
    constructor() {
        effect(() => {
            this.updateEntityForm(this.entityService.entity());
        });
    }

    /**
     * Cancel the current edit operation.
     */
    cancel(): void {
        this.entityService.clear();
    }

    /**
     * Delete the current entity.
     * @param guid The GUID of the entity to delete.
     */
    async delete(guid: string | null): Promise<void> {
        if (guid) {
            await firstValueFrom(this.entitiesService.delete(guid));
        }

        this.searchService.refresh();
        this.entityService.clear();
    }

    /**
     * Save the current entity.
     * @param entity The entity to save.
     */
    async save(): Promise<void> {
        const entity = this.entityForm.getRawValue();

        if (this.entityForm.value) {
            await firstValueFrom(this.entitiesService.createOrUpdate(entity));
        }

        this.searchService.refresh();
        this.entityService.clear();
    }

    /**
     * Update the entity form with the current entity data.
     * @param entity The entity to update the form with.
     */
    private updateEntityForm(entity: Entity | null): void {
        if (entity) {
            this.entityForm.patchValue({
                description: entity.description,
                guid: entity.guid,
                name: entity.name,
            });
        } else {
            this.entityForm.reset();
        }
    }
}
