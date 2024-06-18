import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { BranchSelectComponent } from './branch-select.component';

export default {
  title: 'Libs/Components/BranchSelectComponent',
  component: BranchSelectComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<BranchSelectComponent>;

const Template: Story<BranchSelectComponent> = (
  args: BranchSelectComponent
) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {
  withCreateBranch: false,
};
