import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
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

const Template: StoryFn<DefaultDetailsComponent> = (args: DefaultDetailsComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}
