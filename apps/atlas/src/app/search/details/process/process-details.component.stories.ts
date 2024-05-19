import { Meta, moduleMetadata, StoryFn } from '@storybook/angular';
import { ProcessDetailsComponent } from './process-details.component';

export default {
  title: 'Apps/Atlas/Components/Search/Details/Process/ProcessDetailsComponent',
  component: ProcessDetailsComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<ProcessDetailsComponent>;

const Template: StoryFn<ProcessDetailsComponent> = (
  args: ProcessDetailsComponent
) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {};
