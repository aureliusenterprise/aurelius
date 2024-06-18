import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { ConflictResolutionTemplateSelectComponent } from './conflict-resolution-template-select.component';

export default {
  title: 'Libs/Components/ConflictResolutionTemplateSelectComponent',
  component: ConflictResolutionTemplateSelectComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<ConflictResolutionTemplateSelectComponent>;

const Template: Story<ConflictResolutionTemplateSelectComponent> = (
  args: ConflictResolutionTemplateSelectComponent
) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {
  allowManual: false,
};
