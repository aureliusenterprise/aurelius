import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { EditEntityComponent } from './edit-entity.component';

export default {
  title: 'Apps/Atlas/Components/Search/Editor/EditEntityComponent',
  component: EditEntityComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<EditEntityComponent>;

const Template: Story<EditEntityComponent> = (args: EditEntityComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}