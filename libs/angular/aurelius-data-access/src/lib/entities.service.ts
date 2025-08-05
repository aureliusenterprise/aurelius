import { HttpClient } from "@angular/common/http";
import { inject, Injectable } from "@angular/core";
import { Observable } from "rxjs";

export type Entity = {
    /**
     * The unique identifier for the entity.
     */
    readonly guid?: string | null;

    /**
     * The name of the entity.
     */
    name?: string | null;

    /**
     * The description of the entity.
     */
    description?: string | null;
};

export type FindAllQueryParams = {
    /**
     * The maximum number of entities to return.
     */
    limit?: number;

    /**
     * The search query to filter entities by name or description.
     */
    search?: string;

    /**
     * The number of entities to skip for pagination.
     */
    skip?: number;
};

@Injectable({
    providedIn: "root",
})
export class EntitiesService {
    /**
     * The HTTP client for making API requests.
     */
    private readonly http = inject(HttpClient);

    /**
     * Create a new entity or update an existing one.
     *
     * @param entity The entity to create or update.
     * @returns An observable that emits the created or updated entity.
     */
    createOrUpdate(entity: Entity): Observable<Entity> {
        return this.http.put<Entity>(`/api/entities/`, entity);
    }

    /**
     * Deletes an entity by its GUID.
     *
     * @param guid The unique identifier of the entity to delete.
     * @returns An observable that completes when the entity is deleted.
     */
    delete(guid: string): Observable<void> {
        return this.http.delete<void>(`/api/entities/${guid}`);
    }

    /**
     * Fetches all entities from the API.
     *
     * @param params Optional query parameters for filtering and pagination.
     * @returns An observable that emits the list of entities.
     */
    findAll(params: FindAllQueryParams = {}): Observable<Entity[]> {
        return this.http.get<Entity[]>("/api/entities/", { params });
    }

    /**
     * Fetches a specific entity by its GUID.
     *
     * @param guid The unique identifier of the entity.
     * @returns An observable that emits the entity data.
     */
    findOne(guid: string): Observable<Entity> {
        return this.http.get<Entity>(`/api/entities/${guid}`);
    }
}
