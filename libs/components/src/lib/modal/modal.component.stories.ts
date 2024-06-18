import { Meta, moduleMetadata, Story } from '@storybook/angular';
import { defaultModalContext, ModalComponent } from './modal.component';

export default {
  title: 'Libs/Components/ModalComponent',
  component: ModalComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
} as Meta<ModalComponent>;

const Template: Story<ModalComponent> = (args: ModalComponent) => ({
  props: args,
});

export const Primary = Template.bind({});
Primary.args = {
  context: defaultModalContext,
  isLoading: false,
  active: '',
};
