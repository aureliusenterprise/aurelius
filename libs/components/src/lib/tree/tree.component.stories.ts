import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { TreeComponent } from './tree.component';

export default {
  title: 'Libs/Components/TreeComponent',
  component: TreeComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<TreeComponent>;

const Template: Story<TreeComponent> = (args: TreeComponent) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {
  activeNode: '',
  pathIndex: '',
};
