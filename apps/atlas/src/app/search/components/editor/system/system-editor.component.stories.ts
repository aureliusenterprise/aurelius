import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { SystemEditorComponent } from './system-editor.component';

export default {
  title: 'Apps/Atlas/Components/Search/Components/Editor/SystemEditorComponent',
  component: SystemEditorComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<SystemEditorComponent>;

const Template: StoryFn<SystemEditorComponent> = (args: SystemEditorComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}
