import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { EntityEditorComponent } from './entity-editor.component';

export default {
  title: 'Apps/Atlas/Components/Search/Components/Editor/EntityEditorComponent',
  component: EntityEditorComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<EntityEditorComponent>;

const Template: Story<EntityEditorComponent> = (args: EntityEditorComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}