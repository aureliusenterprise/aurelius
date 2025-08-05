import type { Meta, StoryObj } from "@storybook/angular";
import { Modal } from "./modal.component";

const meta: Meta<Modal> = {
    component: Modal,
    title: "Modal",
};
export default meta;

type Story = StoryObj<Modal>;

const primaryTemplate = `
<aurelius-ui-modal #modal [active]="active" [showCloseButton]="showCloseButton">
    <ng-container modal-content>
        <figure class="image is-square">
            <img
                src="/assets/logo.jpg"
                alt="Modal Image"
            />
        </figure>
    </ng-container>
</aurelius-ui-modal>
<button class="button is-primary" (click)="modal.open()">Open Modal</button>
`;

const emptyTemplate = `
<aurelius-ui-modal #modal [active]="active" [showCloseButton]="showCloseButton"></aurelius-ui-modal>
<button class="button is-primary" (click)="modal.open()">Open Modal</button>
`;

export const Primary: Story = {
    args: {
        active: false,
        showCloseButton: true,
    },
    render: (args) => ({
        props: args,
        template: primaryTemplate,
    }),
};

export const Empty: Story = {
    args: {
        active: false,
        showCloseButton: true,
    },
    render: (args) => ({
        props: args,
        template: emptyTemplate,
    }),
};
