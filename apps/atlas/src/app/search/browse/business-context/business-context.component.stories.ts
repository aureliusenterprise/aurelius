import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { BusinessContextComponent } from './business-context.component';

export default {
  title: 'Apps/Atlas/Components/Search/Browse/Business/BusinessContextComponent',
  component: BusinessContextComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<BusinessContextComponent>;

const Template: StoryFn<BusinessContextComponent> = (args: BusinessContextComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}
