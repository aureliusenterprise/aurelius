import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { DatasetDetailsComponent } from './dataset-details.component';

export default {
  title: 'Apps/Atlas/Components/Search/Details/Dataset/DatasetDetailsComponent',
  component: DatasetDetailsComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<DatasetDetailsComponent>;

const Template: Story<DatasetDetailsComponent> = (args: DatasetDetailsComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}