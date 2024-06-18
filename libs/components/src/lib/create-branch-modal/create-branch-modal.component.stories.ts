import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { CreateBranchModalComponent } from './create-branch-modal.component';

export default {
  title: 'Libs/Components/CreateBranchModalComponent',
  component: CreateBranchModalComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<CreateBranchModalComponent>;

const Template: Story<CreateBranchModalComponent> = (
  args: CreateBranchModalComponent
) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {};
