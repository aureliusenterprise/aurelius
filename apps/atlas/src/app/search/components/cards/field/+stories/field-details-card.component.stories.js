import { RouterTestingModule } from '@angular/router/testing';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import {
  AtlasApiModule,
  ClassificationDefAPIService,
  ElasticApiModule,
  EntityAPIService,
  GovernanceQualitySearchService,
  TypeDefAPIService,
} from '@models4insight/atlas/api';
import { AuthenticationModule } from '@models4insight/authentication';
import { HttpModule } from '@models4insight/http';
import { ReduxModule } from '@models4insight/redux';
import { TaskManagerModule } from '@models4insight/task-manager';
import { TranslateModule } from '@ngx-translate/core';
import { moduleMetadata } from '@storybook/angular';
import { Mermaid } from 'mdx-mermaid/Mermaid';
import { environment } from '../../../../../../environments/environment';
import { DetailsCardComponent } from '../../details-card.component';
import { DetailsCardModule } from '../../details-card.module';
import { FieldDetailsCardModule } from '../field-details-card.module';
import { MockClassficationDefAPIService } from './classification-def-api.mock.service';
import { MockEntityAPIService } from './entity-api.mock.service';
import { MockGovQualityApiService } from './gov-quality-api.mock.service';
import SEARCH_RESULT from './search-result.json';
import { MockTypeDefAPIService } from './type-def-api.mock.service';

export default {
  title:
    'Apps/Atlas/Components/Search/Components/Cards/FieldDetailsCardComponent',

  decorators: [
    moduleMetadata({
      imports: [
        RouterTestingModule,
        FieldDetailsCardModule,
        DetailsCardModule,
        TranslateModule.forRoot(),
        TaskManagerModule,
        FontAwesomeModule,
        ReduxModule.forRoot({
          production: environment.production,
        }),
        HttpModule.forRoot({
          production: environment.production,
        }),
        AuthenticationModule.forRoot(environment.keycloak),
        AtlasApiModule,
        ElasticApiModule.forRoot(environment.atlas),
      ],

      providers: [
        {
          provide: ClassificationDefAPIService,
          useClass: MockClassficationDefAPIService,
        },
        {
          provide: EntityAPIService,
          useClass: MockEntityAPIService,
        },
        {
          provide: GovernanceQualitySearchService,
          useClass: MockGovQualityApiService,
        },
        {
          provide: TypeDefAPIService,
          useClass: MockTypeDefAPIService,
        },
      ],
    }),
  ],

  argTypes: {
    searchResult: {
      control: 'object',
    },
  },
};

export const Primary = {
  render: () => ({
    component: DetailsCardComponent,

    props: {
      searchResult: SEARCH_RESULT,
    },
  }),

  name: 'Primary',
  height: '220px',

  args: {
    searchResult: SEARCH_RESULT,
  },
};
