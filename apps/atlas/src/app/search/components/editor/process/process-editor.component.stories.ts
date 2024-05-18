import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { ProcessEditorComponent } from './process-editor.component';

export default {
  title: 'Apps/Atlas/Components/Search/Components/Editor/ProcessEditorComponent',
  component: ProcessEditorComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<ProcessEditorComponent>;

const Template: Story<ProcessEditorComponent> = (args: ProcessEditorComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}