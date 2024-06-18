import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { SimpleSearchInputComponent } from './simple-search-input.component';

export default {
  title: 'Libs/Components/SimpleSearchInputComponent',
  component: SimpleSearchInputComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<SimpleSearchInputComponent>;

const Template: Story<SimpleSearchInputComponent> = (
  args: SimpleSearchInputComponent
) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {
  query: '',
};
