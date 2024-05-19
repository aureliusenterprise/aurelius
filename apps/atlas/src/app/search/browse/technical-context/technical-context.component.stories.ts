import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { TechnicalContextComponent } from './technical-context.component';

export default {
  title: 'Apps/Atlas/Components/Search/Browse/Technical/TechnicalContextComponent',
  component: TechnicalContextComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<TechnicalContextComponent>;

const Template: StoryFn<TechnicalContextComponent> = (args: TechnicalContextComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}
