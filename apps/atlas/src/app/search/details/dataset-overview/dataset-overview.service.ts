import { HttpErrorResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { GovQualityApiClient } from '@models4insight/atlas/api';
import { firstValueFrom, Observable } from 'rxjs';

/** A related entity: guid, type and display name */
export interface OverviewRef {
    readonly guid: string;
    readonly typeName?: string;
    readonly name: string;
}

/** A classification of an entity; inherited = propagated from the entity `source` */
export interface OverviewClassification {
    readonly typeName: string;
    readonly inherited: boolean;
    readonly source?: string;
}

export interface OverviewAttribute {
    readonly guid: string;
    readonly name: string;
    readonly qualifiedName?: string;
    readonly definition?: string;
    readonly dataEntities: OverviewRef[];
    readonly classifications: OverviewClassification[];
}

export interface OverviewField {
    readonly guid: string;
    readonly name: string;
    readonly qualifiedName?: string;
    readonly fieldType?: string;
    readonly definition?: string;
    readonly attributes: OverviewAttribute[];
    readonly classifications: OverviewClassification[];
}

/** pyatlas /api/aurelius/datasets/{guid}/fields */
export interface DatasetFields {
    readonly dataset: {
        readonly guid: string;
        readonly typeName: string;
        readonly name: string;
        readonly qualifiedName?: string;
        readonly definition?: string;
        readonly collections: OverviewRef[];
    };
    readonly fields: OverviewField[];
    readonly summary: {
        readonly fields: number;
        readonly withAttribute: number;
        readonly withoutAttribute: number;
        readonly attributes: number;
        readonly dataEntities: number;
    };
}

export interface LineageNode {
    readonly guid: string;
    readonly typeName: string;
    readonly kind: 'dataset' | 'process';
    readonly name: string;
    readonly status?: string;
    /** number of fields of an Aurelius dataset (m4i_dataset), otherwise null */
    readonly fieldCount: number | null;
}

/** pyatlas /api/aurelius/datasets/{guid}/lineage: edges in the direction of the data flow */
export interface DatasetLineage {
    readonly baseEntityGuid: string;
    readonly depth: number;
    readonly nodes: LineageNode[];
    readonly edges: { readonly from: string; readonly to: string }[];
    /** false when the dataset has no lineage (the answer then holds only the dataset itself) */
    readonly available?: boolean;
}

/**
 * The dataset overview API of pyatlas, served by the reverse proxy next to the frontend
 * (<tenant>/atlas/dataset_overview/...) with the user's Keycloak token. Answers are kept per dataset while the
 * page is open, so clicking back and forth in the lineage does not load them again.
 */
@Injectable()
export class DatasetOverviewService {
    private readonly path = 'dataset_overview';
    private readonly fieldsCache = new Map<string, Promise<DatasetFields>>();

    constructor(private readonly http: GovQualityApiClient) {}

    fields(guid: string): Promise<DatasetFields> {
        if (!this.fieldsCache.has(guid)) {
            const request = this.call(
                this.http.get<DatasetFields>(`${this.path}/${encodeURIComponent(guid)}/fields`),
            );
            request.catch(() => this.fieldsCache.delete(guid));
            this.fieldsCache.set(guid, request);
        }
        return this.fieldsCache.get(guid);
    }

    lineage(guid: string, depth: number): Promise<DatasetLineage> {
        return this.call(
            this.http.get<DatasetLineage>(`${this.path}/${encodeURIComponent(guid)}/lineage`, {
                params: { depth: String(depth) },
            }),
        );
    }

    private async call<T>(request: Observable<T>): Promise<T> {
        try {
            return await firstValueFrom(request);
        } catch (e) {
            if (e instanceof HttpErrorResponse) {
                throw new Error(e.error?.errorMessage ?? e.message);
            }
            throw e;
        }
    }
}
