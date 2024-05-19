import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { PeopleComponent } from './people.component';

export default {
  title: 'Apps/Atlas/Components/Search/Components/Filter/PeopleComponent',
  component: PeopleComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<PeopleComponent>;

const Template: StoryFn<PeopleComponent> = (args: PeopleComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
    showPlaceholder:  true,
}
