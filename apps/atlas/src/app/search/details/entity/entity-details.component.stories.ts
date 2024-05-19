import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { EntityDetailsComponent } from './entity-details.component';

export default {
  title: 'Apps/Atlas/Components/Search/Details/Entity/EntityDetailsComponent',
  component: EntityDetailsComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<EntityDetailsComponent>;

const Template: StoryFn<EntityDetailsComponent> = (args: EntityDetailsComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}
