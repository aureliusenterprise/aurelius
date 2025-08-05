import { Injectable, signal } from "@angular/core";
import { Entity } from "aurelius-data-access";

@Injectable({
    providedIn: "root",
})
export class EntityService {
    /**
     * The current entity being edited.
     */
    readonly entity = signal<Entity | null>(null);

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
}
