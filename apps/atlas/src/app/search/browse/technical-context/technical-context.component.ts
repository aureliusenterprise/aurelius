import { Component, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import {
  faCompass,
  faInfoCircle,
  faSearch,
  faServer,
} from '@fortawesome/free-solid-svg-icons';
import { AtlasEntitySearchObject } from '@models4insight/atlas/api';
import {
  defaultSimpleSearchInputContext,
  SimpleSearchInputContext,
} from '@models4insight/components';
import { SearchService } from '../../services/search/search.service';
import { TechnicalContextInfoModalComponent } from './info-modal/technical-context-info-modal.component';

const searchBarContext: SimpleSearchInputContext = {
  ...defaultSimpleSearchInputContext,
  label: null,
  placeholder: 'Search for keywords',
};

@Component({
  selector: 'models4insight-technical-context',
  templateUrl: 'technical-context.component.html',
  styleUrls: ['technical-context.component.scss'],
})
export class TechnicalContextComponent {
  readonly faCompass = faCompass;
  readonly faInfoCircle = faInfoCircle;
  readonly faSearch = faSearch;
  readonly faServer = faServer;
  readonly searchBarContext = searchBarContext;

  @ViewChild(TechnicalContextInfoModalComponent, { static: true })
  private readonly infoModal: TechnicalContextInfoModalComponent;

  constructor(
    private readonly router: Router,
    private readonly searchService: SearchService<AtlasEntitySearchObject>
  ) {}

  activateInfoModal() {
    this.infoModal.activate();
  }

  directToTechnical() {
    this.searchService.filters = {
      all: [{ sourcetype: ['Technical'] }, { supertypenames: ['m4i_system'] }],
    };

    this.router.navigate(['/search/results']);
  }

  onQuerySubmitted(query: string) {
    this.searchService.query = '';

    this.searchService.filters = {
      all: [{ sourcetype: ['Technical'] }, { supertypenames: ['m4i_system'] }],
    };

    this.router.navigate(['/search/results'], {
      queryParams: { query },
    });
  }
}
