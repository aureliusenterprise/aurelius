import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { PersonDetailsComponent } from './person-details.component';

export default {
  title: 'Apps/Atlas/Components/Search/Details/Person/PersonDetailsComponent',
  component: PersonDetailsComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<PersonDetailsComponent>;

const Template: StoryFn<PersonDetailsComponent> = (args: PersonDetailsComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}
