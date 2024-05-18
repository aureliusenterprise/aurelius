import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { CheckBoxComponent } from './check-box.component';

export default {
  title: 'Apps/Atlas/Components/Search/Components/Filter/CheckBoxComponent',
  component: CheckBoxComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<CheckBoxComponent>;

const Template: Story<CheckBoxComponent> = (args: CheckBoxComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
    name:  '',
    type:  '',
    count:  '',
}