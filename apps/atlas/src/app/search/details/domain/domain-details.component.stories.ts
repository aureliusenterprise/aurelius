import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { DomainDetailsComponent } from './domain-details.component';

export default {
  title: 'Apps/Atlas/Components/Search/Details/Domain/DomainDetailsComponent',
  component: DomainDetailsComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<DomainDetailsComponent>;

const Template: StoryFn<DomainDetailsComponent> = (args: DomainDetailsComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}
