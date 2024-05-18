import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { FacetComponent } from './facet.component';

export default {
  title: 'Apps/Atlas/Components/Search/Components/Filter/FacetComponent',
  component: FacetComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<FacetComponent>;

const Template: Story<FacetComponent> = (args: FacetComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}