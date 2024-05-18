import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { DataQualityListComponent } from './data-quality-list.component';

export default {
  title: 'Apps/Atlas/Components/Search/Components/DataQualityListComponent',
  component: DataQualityListComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<DataQualityListComponent>;

const Template: Story<DataQualityListComponent> = (args: DataQualityListComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
    showPlaceholder:  true,
}