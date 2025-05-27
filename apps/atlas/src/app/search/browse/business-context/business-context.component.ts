import { Component, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import {
  faChartLine,
  faCompass,
  faInfoCircle,
  faProjectDiagram,
  faSearch
} from '@fortawesome/free-solid-svg-icons';
import {
  AtlasEntitySearchObject
} from '@models4insight/atlas/api';
import {
  defaultSimpleSearchInputContext,
  SimpleSearchInputContext
} from '@models4insight/components';
import { SearchService } from '../../services/search/search.service';
import { BusinessContextInfoModalComponent } from './info-modal/business-context-info-modal.component';

const searchBarContext: SimpleSearchInputContext = {
  ...defaultSimpleSearchInputContext,
  label: null,
  placeholder: 'Search for keywords',
};

@Component({
  selector: 'models4insight-business-context',
  templateUrl: 'business-context.component.html',
  styleUrls: ['business-context.component.scss'],
})
export class BusinessContextComponent {
  readonly faChartLine = faChartLine;
  readonly faCompass = faCompass;
  readonly faInfoCircle = faInfoCircle;
  readonly faProjectDiagram = faProjectDiagram;
  readonly faSearch = faSearch;
  readonly searchBarContext = searchBarContext;

  @ViewChild(BusinessContextInfoModalComponent, { static: true })
  private readonly infoModal: BusinessContextInfoModalComponent;

  constructor(
    private readonly router: Router,
    private readonly searchService: SearchService<AtlasEntitySearchObject>
  ) {}

  activateInfoModal() {
    this.infoModal.activate();
  }

  directToConceptual() {
    this.searchService.query = '';

    this.searchService.filters = {
      all: [
        { sourcetype: ['Business'] },
        { supertypenames: ['m4i_data_domain'] },
      ],
    };

    this.router.navigate(['/search/results']);
  }

  directToDashboard() {
    this.router.navigate(['/dashboard']);
  }

  onQuerySubmitted(query: string) {
    this.searchService.query = query;

    this.searchService.filters = {
      all: [
        { sourcetype: ['Business'] },
      ],
    };

    this.router.navigate(['/search/results'], {
      queryParams: { query },
    });
  }
}
