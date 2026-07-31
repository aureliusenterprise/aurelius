import { Component, OnDestroy, OnInit } from '@angular/core';
import { AtlasEntityDef } from '@models4insight/atlas/api';
import { ModalContext, Select, SelectContext, SortableTableShellConfig } from '@models4insight/components';
import { indexByProperty, untilDestroyed } from '@models4insight/utils';
import { TranslateService } from '@ngx-translate/core';
import { Observable } from 'rxjs';
import { map, switchMap } from 'rxjs/operators';
import { EntityDetailsService } from '../../../services/entity-details/entity-details.service';
import { TypeDefsService } from '../../../services/type-defs/type-defs.service';

const BLACKLISTED_TYPES = new Set(['m4i_referenceable', 'm4i_source']);

function filterReferenceableTypes(entityDefs: AtlasEntityDef[]) {
    const defsByName = indexByProperty(entityDefs, 'name');

    function* generateInheritanceTree(typeName: string): Generator<string> {
        if (!BLACKLISTED_TYPES.has(typeName)) yield typeName;

        const typeDef = defsByName[typeName];

        if (!typeDef) return;

        for (const subType of typeDef.subTypes) {
            yield* generateInheritanceTree(subType);
        }
    }

    const referenceableTypes = new Set(generateInheritanceTree('m4i_referenceable'));

    return Array.from(referenceableTypes)
        .sort()
        .map((typeName) => defsByName[typeName]);
}

const searchModalContext = (translateService: TranslateService): ModalContext => ({
    cancel: translateService.instant('search.details.typeSelect.cancel'),
    confirm: null,
    closeOnConfirm: true,
    title: translateService.instant('search.details.typeSelect.title'),
});

const searchTableConfig = (translateService: TranslateService): SortableTableShellConfig<TypeSelectRow> => ({
    translatedName: {
        displayName: translateService.instant('search.details.typeSelect.translatedName.displayName'),
        description: translateService.instant('search.details.typeSelect.translatedName.description'),
        isNarrow: true,
    },
    description: {
        displayName: translateService.instant('search.details.typeSelect.description.displayName'),
        description: translateService.instant('search.details.typeSelect.description.description'),
        truncate: 'end',
    },
});

interface TypeSelectRow extends AtlasEntityDef {
    readonly translatedName?: string;
}

@Component({
    selector: 'models4insight-type-select',
    templateUrl: 'type-select.component.html',
    styleUrls: ['type-select.component.scss'],
})
export class TypeSelectComponent implements OnInit, OnDestroy {
    readonly control = new Select(false);

    data$: Observable<TypeSelectRow[]>;

    get selectContext(): SelectContext {
        return {
            label: this.translateService.instant('search.details.typeSelect.label'),
            noDataMessage: this.translateService.instant('search.details.typeSelect.noDataMessage'),
            requiredErrorMessage: this.translateService.instant('search.details.typeSelect.requiredErrorMessage'),
            nullInputMessage: this.translateService.instant('search.details.typeSelect.nullInputMessage'),
            searchModalContext: searchModalContext(this.translateService),
            searchTableConfig: searchTableConfig(this.translateService),
        };
    }

    constructor(
        private readonly entityDetailsService: EntityDetailsService,
        private readonly translateService: TranslateService,
        private readonly typeDefsService: TypeDefsService,
    ) {}

    ngOnInit() {
        this.data$ = this.typeDefsService.select(['typeDefs', 'entityDefs']).pipe(
            map((entityDefs) => filterReferenceableTypes(entityDefs)),
            map((entityDefs) => entityDefs.map((def) => this.handleAnnotateEntityDef(def))),
        );

        this.entityDetailsService
            .select(['entityDetails', 'entity', 'typeName'], { includeFalsy: true })
            .pipe(
                switchMap((typeName) => this.getEntityDefByName(typeName)),
                untilDestroyed(this),
            )
            .subscribe((typeDef) => this.updateControlValue(typeDef));

        this.control.valueChanges.pipe(untilDestroyed(this)).subscribe((typeDef) => this.updateEntityType(typeDef));
    }

    ngOnDestroy() {}

    private async getEntityDefByName(typeName: string) {
        const typeDefs = await this.typeDefsService.get(['typeDefs', 'entityDefs']),
            typeDef = typeDefs.find((def) => def.name === typeName);

        return this.handleAnnotateEntityDef(typeDef);
    }

    private handleAnnotateEntityDef(entityDef: AtlasEntityDef): TypeSelectRow {
        if (!entityDef) return null;
        return {
            ...entityDef,
            translatedName: this.translateService.instant(entityDef.name),
        };
    }

    private updateControlValue(typeName: TypeSelectRow) {
        this.control.setValue(typeName, { emitEvent: false });
    }

    private updateEntityType(typeDef: TypeSelectRow) {
        this.entityDetailsService.update({
            description: 'Type selection updated',
            path: ['entityDetails', 'entity', 'typeName'],
            payload: typeDef.name,
        });
    }
}
