import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { BrowseComponent } from './browse.component';

export default {
  title: 'Apps/Atlas/Components/Search/Browse/BrowseComponent',
  component: BrowseComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<BrowseComponent>;

const Template: Story<BrowseComponent> = (args: BrowseComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}