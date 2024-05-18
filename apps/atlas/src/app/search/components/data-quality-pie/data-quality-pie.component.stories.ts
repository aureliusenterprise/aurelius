import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { DataQualityPieComponent } from './data-quality-pie.component';

export default {
  title: 'Apps/Atlas/Components/Search/Components/DataQualityPieComponent',
  component: DataQualityPieComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<DataQualityPieComponent>;

const Template: Story<DataQualityPieComponent> = (args: DataQualityPieComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
    value:  0,
    size:  4,
}