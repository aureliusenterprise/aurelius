import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
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

const Template: StoryFn<CollectionEditorComponent> = (args: CollectionEditorComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}
