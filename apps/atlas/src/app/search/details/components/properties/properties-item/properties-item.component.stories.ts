import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { PropertiesItemComponent } from './properties-item.component';

export default {
  title: 'Apps/Atlas/Components/Search/Details/Components/PropertiesItemComponent',
  component: PropertiesItemComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<PropertiesItemComponent>;

const Template: StoryFn<PropertiesItemComponent> = (args: PropertiesItemComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}
