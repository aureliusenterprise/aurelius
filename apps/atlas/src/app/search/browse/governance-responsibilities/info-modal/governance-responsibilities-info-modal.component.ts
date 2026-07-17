import { Component } from '@angular/core';
import { faUser, IconDefinition } from '@fortawesome/free-solid-svg-icons';
import { AbstractModal, defaultModalContext, ModalContext, SortableTableShellConfig } from '@models4insight/components';

interface TableData {
    readonly description: string;
    readonly icon: IconDefinition;
    readonly typeName: string;
}

const modalContext: ModalContext = {
    ...defaultModalContext,
    title: 'search.browse.governanceContext.infoModal.title',
    confirm: null,
};

const tableConfig: SortableTableShellConfig<TableData> = {
    icon: {
        displayName: 'search.browse.governanceContext.infoModal.iconDisplayName',
        description: 'search.browse.governanceContext.infoModal.iconDescription',
        isNarrow: true,
        isStatic: true,
    },
    typeName: {
        displayName: 'search.browse.governanceContext.infoModal.typeNameDisplayName',
        description: 'search.browse.governanceContext.infoModal.typeNameDescription',
        isNarrow: true,
    },
    description: {
        displayName: 'search.browse.governanceContext.infoModal.descriptionDisplayName',
        description: 'search.browse.governanceContext.infoModal.descriptionDescription',
    },
};

const tableData: TableData[] = [
    {
        description: 'search.browse.governanceContext.infoModal.domainLeadDescription',
        icon: faUser,
        typeName: 'search.browse.governanceContext.infoModal.domainLeadTypeName',
    },
    {
        description: 'search.browse.governanceContext.infoModal.dataOwnerDescription',
        icon: faUser,
        typeName: 'search.browse.governanceContext.infoModal.dataOwnerTypeName',
    },
    {
        description: 'search.browse.governanceContext.infoModal.dataStewardDescription',
        icon: faUser,
        typeName: 'search.browse.governanceContext.infoModal.dataStewardTypeName',
    },
];

@Component({
    selector: 'models4insight-governance-responsibilities-info-modal',
    templateUrl: 'governance-responsibilities-info-modal.component.html',
    styleUrls: ['governance-responsibilities-info-modal.component.scss'],
})
export class GovernanceResponsibilitiesInfoModalComponent extends AbstractModal {
    readonly modalContext = modalContext;
    readonly tableConfig = tableConfig;
    readonly tableData = tableData;
}
