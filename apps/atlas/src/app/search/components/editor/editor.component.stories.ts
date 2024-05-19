import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { EditorComponent } from './editor.component';

export default {
  title: 'Apps/Atlas/Components/Search/Components/Editor/EditorComponent',
  component: EditorComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<EditorComponent>;

const Template: StoryFn<EditorComponent> = (args: EditorComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}
