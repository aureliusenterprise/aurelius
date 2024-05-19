import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { FieldDetailsComponent } from './field-details.component';

export default {
  title: 'Apps/Atlas/Components/Search/Details/Field/FieldDetailsComponent',
  component: FieldDetailsComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<FieldDetailsComponent>;

const Template: StoryFn<FieldDetailsComponent> = (args: FieldDetailsComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}
