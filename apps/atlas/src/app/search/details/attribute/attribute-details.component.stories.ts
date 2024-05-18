import { moduleMetadata, Story, Meta } from '@storybook/angular';
import { AttributeDetailsComponent } from './attribute-details.component';

export default {
  title: 'Apps/Atlas/Components/Search/Details/Attribute/AttributeDetailsComponent',
  component: AttributeDetailsComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    })
  ],
} as Meta<AttributeDetailsComponent>;

const Template: Story<AttributeDetailsComponent> = (args: AttributeDetailsComponent) => ({
  props: args,
});


export const Primary = Template.bind({});
Primary.args = {
}