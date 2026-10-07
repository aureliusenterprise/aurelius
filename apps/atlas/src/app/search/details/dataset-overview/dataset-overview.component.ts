import { Component, ElementRef, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { faHashtag, faProjectDiagram, faSearch, faTable, faTag } from '@fortawesome/free-solid-svg-icons';
import { untilDestroyed } from '@models4insight/utils';
import { distinctUntilChanged, filter, map } from 'rxjs/operators';
import { EntityDetailsService } from '../../services/entity-details/entity-details.service';
import { DatasetFields, DatasetOverviewService, OverviewField } from './dataset-overview.service';
import { layoutLineage, LineageLayout, PlacedNode } from './lineage-layout';

/** One attribute (or several attributes with the same name and description) behind a field */
export interface AttributeGroup {
    readonly name: string;
    /** the first attribute of the group (its name links to it) */
    readonly guid: string;
    readonly definition?: string;
    /** one label per data entity: links to the attribute of that data entity */
    readonly entities: { readonly attributeGuid: string; readonly name: string }[];
    /** the data entities' names, for the label of the description */
    readonly entityNames: string;
}

export interface OverviewRow {
    readonly field: OverviewField;
    readonly groups: AttributeGroup[];
    /** the field's classifications and those of its attributes, by type */
    readonly classifications: { readonly typeName: string; readonly fromAttribute: boolean }[];
    readonly hasPii: boolean;
    readonly longDescription: boolean;
    readonly searchText: string;
}

export type RowFilter = 'all' | 'missing' | 'pii';

const SHOW_CLASSIFICATIONS_KEY = 'aurelius.datasetOverview.showClassifications';
const DEPTH_KEY = 'aurelius.datasetOverview.depth';
const PII = 'PII';

function readSetting(key: string): string | null {
    try {
        return localStorage.getItem(key);
    } catch {
        return null;
    }
}

function writeSetting(key: string, value: string) {
    try {
        localStorage.setItem(key, value);
    } catch {
        /* private mode: keep the setting for this page only */
    }
}

/** Rows of the fields table: attributes with the same name and description shown once, with all data entities */
export function overviewRows(table: DatasetFields): OverviewRow[] {
    return table.fields.map((field) => {
        const groups: { name: string; guid: string; definition?: string; entities: AttributeGroup['entities'] }[] = [];
        for (const a of field.attributes) {
            const key = `${a.name}\u0000${a.definition ?? ''}`;
            let group = groups.find((g) => `${g.name}\u0000${g.definition ?? ''}` === key);
            if (!group) {
                group = { name: a.name, guid: a.guid, definition: a.definition, entities: [] };
                groups.push(group);
            }
            group.entities = [
                ...group.entities,
                ...a.dataEntities.map((e) => ({ attributeGuid: a.guid, name: e.name })),
            ];
        }
        const types = new Map<string, boolean>();
        field.classifications.forEach((c) => types.set(c.typeName, false));
        field.attributes.forEach((a) =>
            a.classifications.forEach((c) => types.set(c.typeName, types.get(c.typeName) ?? true)),
        );
        const attributeGroups: AttributeGroup[] = groups.map((g) => ({
            ...g,
            entityNames: g.entities.map((e) => e.name).join(', '),
        }));
        const classifications = [...types].map(([typeName, fromAttribute]) => ({ typeName, fromAttribute }));
        const searchText = [
            field.name,
            field.fieldType,
            ...field.attributes.map((a) => `${a.name} ${a.definition ?? ''} ${a.dataEntities.map((e) => e.name).join(' ')}`),
        ]
            .join(' ')
            .toLowerCase();
        return {
            field,
            groups: attributeGroups,
            classifications,
            hasPii: types.has(PII),
            longDescription: groups.length > 1 || groups.some((g) => (g.definition ?? '').length > 160),
            searchText,
        };
    });
}

/**
 * The overview of a dataset: its lineage on top (clickable) and below a table of the selected dataset's fields with
 * the attribute behind each field, the attribute's description and data entities. Clicking a process shows what it
 * reads and writes. The data comes from pyatlas, which walks dataset -> fields -> attributes -> data entities.
 */
@Component({
    selector: 'models4insight-dataset-overview',
    templateUrl: 'dataset-overview.component.html',
    styleUrls: ['dataset-overview.component.scss'],
    providers: [DatasetOverviewService],
})
export class DatasetOverviewComponent implements OnInit, OnDestroy {
    readonly faHashtag = faHashtag;
    readonly faProjectDiagram = faProjectDiagram;
    readonly faSearch = faSearch;
    readonly faTable = faTable;
    readonly faTag = faTag;

    readonly depthOptions = [1, 2, 3, 5, 10];
    depth = Number(readSetting(DEPTH_KEY)) || 5;

    baseGuid: string;
    baseName: string;

    layout: LineageLayout;
    isLoadingLineage = false;
    lineageError: string = null;

    selected: PlacedNode;
    table: DatasetFields;
    rows: OverviewRow[] = [];
    isLoadingTable = false;
    tableError: string = null;

    query = '';
    rowFilter: RowFilter = 'all';
    showClassifications = readSetting(SHOW_CLASSIFICATIONS_KEY) !== 'false';
    readonly expanded = new Set<string>();

    @ViewChild('lineageScroll') private readonly lineageScroll: ElementRef<HTMLElement>;

    private tableRequest = 0;

    constructor(
        private readonly entityDetailsService: EntityDetailsService,
        private readonly api: DatasetOverviewService,
    ) {}

    ngOnInit() {
        this.entityDetailsService.entityDetails$
            .pipe(
                filter((entity) => !!entity?.guid),
                map((entity) => ({ guid: entity.guid, name: entity.attributes?.name ?? entity.attributes?.qualifiedName })),
                distinctUntilChanged((a, b) => a.guid === b.guid),
                untilDestroyed(this),
            )
            .subscribe(({ guid, name }) => {
                this.baseGuid = guid;
                this.baseName = name;
                this.loadLineage();
            });
    }

    ngOnDestroy() {}

    // ------------------------------------------------------------------ lineage
    async loadLineage() {
        this.isLoadingLineage = true;
        this.lineageError = null;
        try {
            this.layout = layoutLineage(await this.api.lineage(this.baseGuid, this.depth));
            const keep = this.selected && this.layout.nodes.find((n) => n.guid === this.selected.guid);
            this.select(keep ?? this.layout.nodes.find((n) => n.guid === this.baseGuid));
            setTimeout(() => this.scrollToBase());
        } catch (e) {
            this.layout = null;
            this.lineageError = e.message;
            this.select(null);
        } finally {
            this.isLoadingLineage = false;
        }
    }

    changeDepth(depth: number) {
        this.depth = Number(depth);
        writeSetting(DEPTH_KEY, String(this.depth));
        this.loadLineage();
    }

    private scrollToBase() {
        const scroller = this.lineageScroll?.nativeElement;
        const base = this.layout?.nodes.find((n) => n.guid === this.baseGuid);
        if (scroller && base) {
            scroller.scrollLeft = Math.max(0, base.x + base.width / 2 - scroller.clientWidth / 2);
        }
    }

    // ------------------------------------------------------------------ selection
    get isDatasetSelected() {
        return this.selected?.kind === 'dataset';
    }

    get isProcessSelected() {
        return this.selected?.kind === 'process';
    }

    get baseNode(): PlacedNode | undefined {
        return this.layout?.nodes.find((n) => n.guid === this.baseGuid);
    }

    get selectedIsBase() {
        return this.selected?.guid === this.baseGuid;
    }

    /** A dataset of another type than an Aurelius dataset: no fields to show */
    get selectedHasNoTable() {
        return this.isDatasetSelected && this.selected.fieldCount === null;
    }

    select(node: PlacedNode | null | undefined) {
        // the base entity itself when the lineage could not be loaded
        this.selected = node ?? null;
        this.query = '';
        this.rowFilter = 'all';
        this.expanded.clear();
        if (!node && this.baseGuid) {
            this.loadTable(this.baseGuid);
        } else if (node?.kind === 'dataset' && node.fieldCount !== null) {
            this.loadTable(node.guid);
        } else {
            this.table = null;
            this.rows = [];
        }
    }

    selectByGuid(guid: string) {
        this.select(this.layout?.nodes.find((n) => n.guid === guid));
    }

    backToBase() {
        this.selectByGuid(this.baseGuid);
    }

    inputsOf(node: PlacedNode): PlacedNode[] {
        return this.layout.edges
            .filter((e) => e.to === node.guid)
            .map((e) => this.layout.nodes.find((n) => n.guid === e.from));
    }

    outputsOf(node: PlacedNode): PlacedNode[] {
        return this.layout.edges
            .filter((e) => e.from === node.guid)
            .map((e) => this.layout.nodes.find((n) => n.guid === e.to));
    }

    private async loadTable(guid: string) {
        const request = ++this.tableRequest;
        this.isLoadingTable = true;
        this.tableError = null;
        try {
            const table = await this.api.fields(guid);
            if (request === this.tableRequest) {
                this.table = table;
                this.rows = overviewRows(table);
            }
        } catch (e) {
            if (request === this.tableRequest) {
                this.table = null;
                this.rows = [];
                this.tableError = e.message;
            }
        } finally {
            if (request === this.tableRequest) {
                this.isLoadingTable = false;
            }
        }
    }

    // ------------------------------------------------------------------ table
    get visibleRows(): OverviewRow[] {
        const q = this.query.trim().toLowerCase();
        return this.rows.filter(
            (row) =>
                (this.rowFilter !== 'missing' || row.groups.length === 0) &&
                (this.rowFilter !== 'pii' || row.hasPii) &&
                (!q || row.searchText.includes(q)),
        );
    }

    get piiCount() {
        return this.rows.filter((r) => r.hasPii).length;
    }

    setFilter(rowFilter: RowFilter) {
        this.rowFilter = rowFilter;
    }

    toggleClassifications() {
        this.showClassifications = !this.showClassifications;
        writeSetting(SHOW_CLASSIFICATIONS_KEY, String(this.showClassifications));
    }

    toggleRow(guid: string) {
        if (this.expanded.has(guid)) {
            this.expanded.delete(guid);
        } else {
            this.expanded.add(guid);
        }
    }

    trackByGuid(_: number, item: { guid?: string; field?: OverviewField }) {
        return item.guid ?? item.field?.guid;
    }
}
