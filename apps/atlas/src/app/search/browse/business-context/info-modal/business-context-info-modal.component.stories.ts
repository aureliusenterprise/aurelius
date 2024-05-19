import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { BusinessContextInfoModalComponent } from './business-context-info-modal.component';

export default {
  title: 'Apps/Atlas/Components/Search/Browse/Business/BusinessContextInfoModalComponent',
  component: BusinessContextInfoModalComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<BusinessContextInfoModalComponent>;

const Template: StoryFn<BusinessContextInfoModalComponent> = (args: BusinessContextInfoModalComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}
