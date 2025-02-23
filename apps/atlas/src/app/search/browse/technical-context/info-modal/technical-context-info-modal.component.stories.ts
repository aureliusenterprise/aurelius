import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { TechnicalContextInfoModalComponent } from './technical-context-info-modal.component';

export default {
  title: 'Apps/Atlas/Components/Search/Browse/Technical/TechnicalContextInfoModalComponent',
  component: TechnicalContextInfoModalComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<TechnicalContextInfoModalComponent>;

const Template: StoryFn<TechnicalContextInfoModalComponent> = (args: TechnicalContextInfoModalComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}
