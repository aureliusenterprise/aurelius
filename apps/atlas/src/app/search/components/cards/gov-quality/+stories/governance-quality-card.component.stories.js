import { RouterTestingModule } from '@angular/router/testing';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import {
  AtlasApiModule,
  ClassificationDefAPIService,
  ElasticApiModule,
  EntityAPIService,
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
import { SHOW_GOV_QUALITY } from '../../config';
import { GovernanceQualityCardModule } from '../governance-quality-card.module';
import { MockEntityAPIService } from './entity-api.mock.service';
import SEARCH_RESULT from './search-result.json';
import { MockTypeDefAPIService } from './type-def-api.mock.service';

export default {
  title:
    'Apps/Atlas/Components/Search/Components/Cards/GovernanceQualityCardComponent',

  decorators: [
    moduleMetadata({
      imports: [
        RouterTestingModule,
        GovernanceQualityCardModule,
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
          provide: EntityAPIService,
          useClass: MockEntityAPIService,
        },
        {
          provide: SHOW_GOV_QUALITY,
          useValue: false,
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
  height: '143px',

  args: {
    searchResult: SEARCH_RESULT,
  },
};
