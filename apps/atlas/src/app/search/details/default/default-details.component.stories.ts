import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { DefaultDetailsComponent } from './default-details.component';

export default {
  title: 'Apps/Atlas/Components/Search/Details/Default/DefaultDetailsComponent',
  component: DefaultDetailsComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<DefaultDetailsComponent>;

const Template: Story<DefaultDetailsComponent> = (args: DefaultDetailsComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}