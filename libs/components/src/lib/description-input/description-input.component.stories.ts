import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { DescriptionInputComponent } from './description-input.component';

export default {
  title: 'Libs/Components/DescriptionInputComponent',
  component: DescriptionInputComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<DescriptionInputComponent>;

const Template: Story<DescriptionInputComponent> = (
  args: DescriptionInputComponent
) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {};
