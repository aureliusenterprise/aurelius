import { moduleMetadata, StoryFn, Meta } from '@storybook/angular';
import { TypeSelectComponent } from './type-select.component';

export default {
  title: 'Apps/Atlas/Components/Search/Components/Editor/TypeSelectComponent',
  component: TypeSelectComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<TypeSelectComponent>;

const Template: StoryFn<TypeSelectComponent> = (args: TypeSelectComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}
