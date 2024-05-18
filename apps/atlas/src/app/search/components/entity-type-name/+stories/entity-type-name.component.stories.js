import { TranslateModule } from '@ngx-translate/core';
import { moduleMetadata } from '@storybook/angular';
import { Mermaid } from 'mdx-mermaid/Mermaid';
import { MockEntityDetailsService } from './entity-details.mock.service.ts';
import { EntityTypeNameComponent } from '../entity-type-name.component';
import { EntityTypeNameModule } from '../entity-type-name.module';
import { EntityDetailsService } from '../../../services/entity-details/entity-details.service';

export default {
  title:
    'Apps/Atlas/Components/Search/Components/Type name/EntityTypeNameComponent',

  decorators: [
    moduleMetadata({
      imports: [EntityTypeNameModule, TranslateModule.forRoot()],

      providers: [
        {
          provide: EntityDetailsService,
          useClass: MockEntityDetailsService,
        },
      ],
    }),
  ],

  argTypes: {
    showBaseTypeName: {
      control: 'boolean',
    },

    showIcon: {
      control: 'boolean',
    },

    showTypeName: {
      control: 'boolean',
    },
  },
};

export const Primary = {
  render: () => ({
    component: EntityTypeNameComponent,
  }),

  name: 'Primary',
  height: '56px',
};
