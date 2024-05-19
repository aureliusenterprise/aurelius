import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { TermComponent } from './term.component';

export default {
  title: 'Apps/Atlas/Components/Search/Components/Filter/TermComponent',
  component: TermComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<TermComponent>;

const Template: StoryFn<TermComponent> = (args: TermComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
    guid:  '',
}
