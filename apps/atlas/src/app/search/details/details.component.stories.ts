import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { DetailsComponent } from './details.component';

export default {
  title: 'Apps/Atlas/Components/Search/Details/DetailsComponent',
  component: DetailsComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<DetailsComponent>;

const Template: Story<DetailsComponent> = (args: DetailsComponent) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {};
