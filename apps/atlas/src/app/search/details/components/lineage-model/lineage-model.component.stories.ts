import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { LineageModelComponent } from './lineage-model.component';

export default {
  title: 'Apps/Atlas/Components/Search/Details/Components/LineageModelComponent',
  component: LineageModelComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<LineageModelComponent>;

const Template: Story<LineageModelComponent> = (args: LineageModelComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}