import { TranslateModule } from '@ngx-translate/core';
import { moduleMetadata } from '@storybook/angular';
import { Mermaid } from 'mdx-mermaid/Mermaid';
import { TypeNameComponent } from '../type-name.component';
import { TypeNameModule } from '../type-name.module';

export default {
  title: 'Apps/Atlas/Components/Search/Components/Type name/TypeNameComponent',

  decorators: [
    moduleMetadata({
      imports: [TypeNameModule, TranslateModule.forRoot()],
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

    typeAlias: {
      control: 'text',
    },

    typeName: {
      control: 'text',
    },
  },
};

export const Primary = {
  render: () => ({
    component: TypeNameComponent,

    props: {
      typeName: 'm4i_data_domain',
    },
  }),

  name: 'Primary',
  height: '56px',
};

export const TypeAlias = {
  render: () => ({
    component: TypeNameComponent,

    props: {
      typeAlias: 'Department',
      typeName: 'm4i_data_domain',
    },
  }),

  name: 'Type alias',
  height: '56px',
};

export const ShowBaseType = {
  render: () => ({
    component: TypeNameComponent,

    props: {
      showBaseTypeName: true,
      typeAlias: 'Department',
      typeName: 'm4i_data_domain',
    },
  }),

  name: 'Show base type',
  height: '56px',
};

export const HideIcon = {
  render: () => ({
    component: TypeNameComponent,

    props: {
      showIcon: false,
      typeName: 'm4i_data_domain',
    },
  }),

  name: 'Hide icon',
  height: '56px',
};

export const HideTypeName = {
  render: () => ({
    component: TypeNameComponent,

    props: {
      showTypeName: false,
      typeName: 'm4i_data_domain',
    },
  }),

  name: 'Hide type name',
  height: '56px',
};
