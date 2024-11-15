import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { SearchComponent } from './search.component';

export default {
  title: 'Apps/Atlas/Components/Search/SearchComponent',
  component: SearchComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<SearchComponent>;

const Template: StoryFn<SearchComponent> = (args: SearchComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}
