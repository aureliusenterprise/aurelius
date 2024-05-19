import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { DescriptionComponent } from './description.component';

export default {
  title: 'Apps/Atlas/Components/Search/Components/DescriptionComponent',
  component: DescriptionComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<DescriptionComponent>;

const Template: StoryFn<DescriptionComponent> = (args: DescriptionComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
    showPlaceholder:  true,
    truncate:  true,
}
