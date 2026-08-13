import { Component } from '@angular/core';
import { faProjectDiagram, faServer, faTable, faTag, IconDefinition } from '@fortawesome/free-solid-svg-icons';
import { AbstractModal, defaultModalContext, ModalContext, SortableTableShellConfig } from '@models4insight/components';

interface TableData {
    readonly description: string;
    readonly icon: IconDefinition;
    readonly typeName: string;
}

const modalContext: ModalContext = {
    ...defaultModalContext,
    title: 'search.browse.technicalContext.infoModal.title',
    confirm: null,
};

const tableConfig: SortableTableShellConfig<TableData> = {
    icon: {
        displayName: 'search.browse.technicalContext.infoModal.iconDisplayName',
        description: 'search.browse.technicalContext.infoModal.iconDescription',
        isNarrow: true,
        isStatic: true,
    },
    typeName: {
        displayName: 'search.browse.technicalContext.infoModal.typeNameDisplayName',
        description: 'search.browse.technicalContext.infoModal.typeNameDescription',
        isNarrow: true,
    },
    description: {
        displayName: 'search.browse.technicalContext.infoModal.descriptionDisplayName',
        description: 'search.browse.technicalContext.infoModal.descriptionDescription',
    },
};

const tableData: TableData[] = [
    {
        description: 'search.browse.technicalContext.infoModal.systemDescription',
        icon: faServer,
        typeName: 'm4i_system',
    },
    {
        description: 'search.browse.technicalContext.infoModal.collectionDescription',
        icon: faProjectDiagram,
        typeName: 'm4i_collection',
    },
    {
        description: 'search.browse.technicalContext.infoModal.datasetDescription',
        icon: faTable,
        typeName: 'm4i_dataset',
    },
    {
        description: 'search.browse.technicalContext.infoModal.fieldDescription',
        icon: faTag,
        typeName: 'm4i_field',
    },
];

@Component({
    selector: 'models4insight-technical-context-info-modal',
    templateUrl: 'technical-context-info-modal.component.html',
    styleUrls: ['technical-context-info-modal.component.scss'],
})
export class TechnicalContextInfoModalComponent extends AbstractModal {
    readonly modalContext = modalContext;
    readonly tableConfig = tableConfig;
    readonly tableData = tableData;
}
