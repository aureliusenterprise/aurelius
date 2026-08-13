import { Component } from '@angular/core';
import { faProjectDiagram, faTable, faTag, IconDefinition } from '@fortawesome/free-solid-svg-icons';
import { AbstractModal, defaultModalContext, ModalContext, SortableTableShellConfig } from '@models4insight/components';

interface TableData {
    readonly description: string;
    readonly icon: IconDefinition;
    readonly typeName: string;
}

const modalContext: ModalContext = {
    ...defaultModalContext,
    title: 'search.browse.businessContext.infoModal.title',
    confirm: null,
};

const tableConfig: SortableTableShellConfig<TableData> = {
    icon: {
        displayName: 'search.browse.businessContext.infoModal.iconDisplayName',
        description: 'search.browse.businessContext.infoModal.iconDescription',
        isNarrow: true,
        isStatic: true,
    },
    typeName: {
        displayName: 'search.browse.businessContext.infoModal.typeNameDisplayName',
        description: 'search.browse.businessContext.infoModal.typeNameDescription',
        isNarrow: true,
    },
    description: {
        displayName: 'search.browse.businessContext.infoModal.descriptionDisplayName',
        description: 'search.browse.businessContext.infoModal.descriptionDescription',
    },
};

const tableData: TableData[] = [
    {
        description: 'search.browse.businessContext.infoModal.dataDomainDescription',
        icon: faProjectDiagram,
        typeName: 'm4i_data_domain',
    },
    {
        description: 'search.browse.businessContext.infoModal.dataEntityDescription',
        icon: faTable,
        typeName: 'm4i_data_entity',
    },
    {
        description: 'search.browse.businessContext.infoModal.dataAttributeDescription',
        icon: faTag,
        typeName: 'm4i_data_attribute',
    },
];

@Component({
    selector: 'models4insight-business-context-info-modal',
    templateUrl: 'business-context-info-modal.component.html',
    styleUrls: ['business-context-info-modal.component.scss'],
})
export class BusinessContextInfoModalComponent extends AbstractModal {
    readonly modalContext = modalContext;
    readonly tableConfig = tableConfig;
    readonly tableData = tableData;
}
