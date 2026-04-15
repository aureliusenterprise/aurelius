import { inject, Injectable, signal } from "@angular/core";
import { takeUntilDestroyed } from "@angular/core/rxjs-interop";
import { EntitiesService, Entity, Envelope } from "aurelius-data-access";

@Injectable({
    providedIn: "root",
})
export class EntityService {
    /**
     * The current entity being edited.
     */
    readonly entity = signal<Entity | null>(null);

    private readonly entitiesService = inject(EntitiesService);

    constructor() {
        /**
         * Whenever an entity is created or updated, check if it's the current entity and update it if so.
         */
        this.entitiesService.entities$
            .pipe(takeUntilDestroyed())
            .subscribe((envelope) => this.handleEntityUpdate(envelope));
    }

    /**
     * Clear the current entity.
     */
    clear(): void {
        this.entity.set(null);
    }

    /**
     * Create a new entity with default values.
     */
    create(): void {
        this.entity.set({ guid: undefined, name: "", description: "" });
    }

    /**
     * Edit an existing entity.
     * @param entity The entity to edit.
     */
    edit(entity: Entity): void {
        this.entity.set(entity);
    }

    /**
     * Handle an entity update received from the server. If the updated entity is the current entity, update it in the signal. If the updated entity is deleted (value is null), clear the signal.
     * @param envelope The envelope containing the updated entity or null if deleted.
     */
    private handleEntityUpdate(envelope: Envelope<Entity | null>): void {
        const current = this.entity();

        if (current?.guid !== envelope.guid) {
            return;
        }

        const entity = envelope.value;

        if (entity) {
            this.edit(entity);
        } else {
            this.clear();
        }
    }
}
