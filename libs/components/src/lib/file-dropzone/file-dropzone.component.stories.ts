import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { FileDropzoneComponent } from './file-dropzone.component';

export default {
  title: 'Libs/Components/FileDropzoneComponent',
  component: FileDropzoneComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<FileDropzoneComponent>;

const Template: Story<FileDropzoneComponent> = (
  args: FileDropzoneComponent
) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {};
