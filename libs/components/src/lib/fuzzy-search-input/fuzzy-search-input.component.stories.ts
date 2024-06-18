import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { FuzzySearchInputComponent } from './fuzzy-search-input.component';

export default {
  title: 'Libs/Components/FuzzySearchInputComponent',
  component: FuzzySearchInputComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<FuzzySearchInputComponent>;

const Template: Story<FuzzySearchInputComponent> = (
  args: FuzzySearchInputComponent
) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {
  query: '',
  tokenizerConfig: '',
  searchItems: '',
};
