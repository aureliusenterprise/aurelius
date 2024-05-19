import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { CreateEntityComponent } from './create-entity.component';

export default {
  title: 'Apps/Atlas/Components/Search/Editor/CreateEntityComponent',
  component: CreateEntityComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<CreateEntityComponent>;

const Template: StoryFn<CreateEntityComponent> = (args: CreateEntityComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}
