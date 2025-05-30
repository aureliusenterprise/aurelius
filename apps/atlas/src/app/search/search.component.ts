import { Component, OnInit, ViewChild } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { faPlus } from '@fortawesome/free-solid-svg-icons';
import {
  defaultSimpleSearchInputContext,
  SimpleSearchInputContext,
} from '@models4insight/components';
import { Observable } from 'rxjs';
import { filter } from 'rxjs/operators';
import { EditorComponent } from './components/editor/editor.component';
import { EntitySearchService } from './services/search/entity-search.service';

const searchBarContext: SimpleSearchInputContext = {
  ...defaultSimpleSearchInputContext,
  label: null,
  placeholder: 'Type your search',
};

@Component({
  selector: 'models4insight-search',
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.scss'],
})
export class SearchComponent implements OnInit {
  @ViewChild(EditorComponent, { static: true })
  readonly editor: EditorComponent;

  readonly faPlus = faPlus;
  readonly searchBarContext = searchBarContext;

  readonly query$: Observable<string>;

  constructor(
    private readonly router: Router,
    private readonly searchService: EntitySearchService
  ) {
    this.query$ = this.searchService.select(['queryObject', 'query']);
  }

  ngOnInit() {
    this.router.events
      .pipe(filter((event) => event instanceof NavigationEnd))
      .subscribe((event: NavigationEnd) => {
        if (event.urlAfterRedirects.includes('/search/browse')) {
          this.searchService.reset();
        }
      });
  }

  onQuerySubmitted(query: string) {
    this.searchService.filters = {};
    this.router.navigate(['/search/results'], {
      queryParams: { query },
    });
  }

  redirectToEditor() {
    this.router.navigate(['/search/create-entity']);
    this.editor?.activate();
  }
}
