import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { DatasetEditorComponent } from './dataset-editor.component';

export default {
  title: 'Apps/Atlas/Components/Search/Components/Editor/DatasetEditorComponent',
  component: DatasetEditorComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<DatasetEditorComponent>;

const Template: Story<DatasetEditorComponent> = (args: DatasetEditorComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}