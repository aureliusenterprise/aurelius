import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { CompareModalComponent } from './compare-modal.component';

export default {
  title: 'Libs/Components/CompareModalComponent',
  component: CompareModalComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<CompareModalComponent>;

const Template: Story<CompareModalComponent> = (
  args: CompareModalComponent
) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {};
