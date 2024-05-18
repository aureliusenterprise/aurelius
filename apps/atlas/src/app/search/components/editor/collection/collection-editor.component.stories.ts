import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { CollectionEditorComponent } from './collection-editor.component';

export default {
  title: 'Apps/Atlas/Components/Search/Components/Editor/CollectionEditorComponent',
  component: CollectionEditorComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<CollectionEditorComponent>;

const Template: Story<CollectionEditorComponent> = (args: CollectionEditorComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}