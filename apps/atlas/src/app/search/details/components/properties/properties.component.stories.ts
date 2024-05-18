import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { PropertiesComponent } from './properties.component';

export default {
  title: 'Apps/Atlas/Components/Search/Details/Components/PropertiesComponent',
  component: PropertiesComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<PropertiesComponent>;

const Template: Story<PropertiesComponent> = (args: PropertiesComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}