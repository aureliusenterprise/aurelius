import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { SystemDetailsComponent } from './system-details.component';

export default {
  title: 'Apps/Atlas/Components/Search/Details/System/SystemDetailsComponent',
  component: SystemDetailsComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<SystemDetailsComponent>;

const Template: StoryFn<SystemDetailsComponent> = (args: SystemDetailsComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}
