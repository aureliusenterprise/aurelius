import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { ArchimateIconComponent } from './archimate-icon.component';

export default {
  title: 'Libs/Components/ArchimateIconComponent',
  component: ArchimateIconComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<ArchimateIconComponent>;

const Template: Story<ArchimateIconComponent> = (
  args: ArchimateIconComponent
) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {
  type: '',
};
