import { Component, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import { faCompass, faInfoCircle, faProjectDiagram, faSearch, faUser } from '@fortawesome/free-solid-svg-icons';
import { AtlasEntitySearchObject } from '@models4insight/atlas/api';
import { AuthenticationService } from '@models4insight/authentication';
import { defaultSimpleSearchInputContext, SimpleSearchInputContext } from '@models4insight/components';
import { SearchService } from '../../services/search/search.service';
import { GovernanceResponsibilitiesInfoModalComponent } from './info-modal/governance-responsibilities-info-modal.component';
import { TranslateService } from '@ngx-translate/core';
import { map, Observable } from 'rxjs';

const searchBarContext: SimpleSearchInputContext = {
    ...defaultSimpleSearchInputContext,
    label: null,
    placeholder: 'Search by name or email',
};

@Component({
    selector: 'models4insight-governance-responsibilities',
    templateUrl: 'governance-responsibilities.component.html',
    styleUrls: ['governance-responsibilities.component.scss'],
})
export class GovernanceResponsibilitiesComponent {
    readonly faCompass = faCompass;
    readonly faInfoCircle = faInfoCircle;
    readonly faProjectDiagram = faProjectDiagram;
    readonly faSearch = faSearch;
    readonly searchBarContext: Observable<SimpleSearchInputContext>;
    readonly faUser = faUser;

    @ViewChild(GovernanceResponsibilitiesInfoModalComponent, { static: true })
    private readonly infoModal: GovernanceResponsibilitiesInfoModalComponent;

    constructor(
        private readonly authenticationService: AuthenticationService,
        private readonly router: Router,
        private readonly searchService: SearchService<AtlasEntitySearchObject>,
        private readonly translateService: TranslateService,
    ) {
        this.searchBarContext = this.translateService
            .get('search.browse.governanceContext.searchPlaceholder')
            .pipe(map((translation) => ({ ...searchBarContext, placeholder: translation })));
    }

    activateInfoModal() {
        this.infoModal.activate();
    }

    directToPeople() {
        this.searchService.filters = {
            all: [{ typename: ['m4i_person'] }],
        };

        this.router.navigate(['/search/results']);
    }

    onQuerySubmitted(query: string) {
        this.searchService.query = '';

        this.searchService.filters = {
            all: [{ typename: ['m4i_person'] }],
        };

        this.router.navigate(['/search/results'], {
            queryParams: { query },
        });
    }

    async directToUser() {
        const email = await this.authenticationService.get(['credentials', 'email']);

        this.searchService.filters = {
            all: [{ typename: ['m4i_person'] }],
        };

        this.searchService.query = email;

        this.router.navigate(['/search/results'], {
            queryParams: { query: email },
        });
    }
}
