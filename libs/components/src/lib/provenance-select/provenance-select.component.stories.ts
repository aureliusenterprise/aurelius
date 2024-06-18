import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { ProvenanceSelectComponent } from './provenance-select.component';

export default {
  title: 'Libs/Components/ProvenanceSelectComponent',
  component: ProvenanceSelectComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<ProvenanceSelectComponent>;

const Template: Story<ProvenanceSelectComponent> = (
  args: ProvenanceSelectComponent
) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {};
