import { Meta, moduleMetadata, Story } from '@storybook/angular';
import { DomainsComponent } from './domains.component';

export default {
  title: 'Apps/Atlas/Components/Dashboards/Domains/DomainsComponent',
  component: DomainsComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<DomainsComponent>;

const Template: Story<DomainsComponent> = (args: DomainsComponent) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {};
