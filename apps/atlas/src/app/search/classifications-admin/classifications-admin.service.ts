import { HttpErrorResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { GovQualityApiClient } from '@models4insight/atlas/api';
import { firstValueFrom, Observable } from 'rxjs';

/** A classification as the management page shows it (pyatlas /api/aurelius/classifications) */
export interface ClassificationSummary {
    readonly name: string;
    readonly displayName?: string;
    readonly displayNames?: { readonly [language: string]: string };
    readonly description?: string;
    readonly entityTypes: string[];
    readonly createdBy?: string;
    readonly updatedBy?: string;
    readonly updateTime?: number;
    readonly usage: { readonly direct: number; readonly propagated: number };
}

export interface ClassificationInput {
    name: string;
    displayName: string;
    displayNames: { [language: string]: string };
    description: string;
    entityTypes: string[];
}

/** An error the administrator can correct, with the form field it belongs to */
export class ClassificationRequestError extends Error {
    constructor(
        message: string,
        readonly field?: string,
    ) {
        super(message);
    }
}

/**
 * The classification management API of pyatlas, served by the reverse proxy next to the frontend
 * (<tenant>/atlas/classifications) with the user's Keycloak token.
 */
@Injectable()
export class ClassificationsAdminService {
    private readonly path = 'classifications';

    constructor(private readonly http: GovQualityApiClient) {}

    list(): Promise<ClassificationSummary[]> {
        return this.call(this.http.get<ClassificationSummary[]>(this.path));
    }

    create(input: ClassificationInput): Promise<ClassificationSummary> {
        return this.call(this.http.post<ClassificationSummary>(this.path, input));
    }

    update(name: string, input: ClassificationInput): Promise<ClassificationSummary> {
        return this.call(this.http.put<ClassificationSummary>(`${this.path}/${encodeURIComponent(name)}`, input));
    }

    delete(name: string): Promise<void> {
        return this.call(this.http.delete<void>(`${this.path}/${encodeURIComponent(name)}`));
    }

    private async call<T>(request: Observable<T>): Promise<T> {
        try {
            return await firstValueFrom(request);
        } catch (e) {
            if (e instanceof HttpErrorResponse) {
                const body = e.error ?? {};
                throw new ClassificationRequestError(
                    body.errorMessage || body.msgDesc || `${e.status} ${e.statusText}`,
                    body.field || undefined,
                );
            }
            throw e;
        }
    }
}
