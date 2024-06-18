import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { BranchNameInputComponent } from './branch-name-input.component';

export default {
  title: 'Libs/Components/BranchNameInputComponent',
  component: BranchNameInputComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<BranchNameInputComponent>;

const Template: Story<BranchNameInputComponent> = (
  args: BranchNameInputComponent
) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {
  inputClasses: [],
};
