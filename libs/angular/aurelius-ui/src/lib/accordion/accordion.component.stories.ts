import type { Meta, StoryObj } from "@storybook/angular";
import { Accordion } from "./accordion.component";

const meta: Meta<Accordion> = {
    component: Accordion,
    title: "Accordion",
};
export default meta;

type Story = StoryObj<Accordion>;

const primaryTemplate = `
<aurelius-ui-accordion [expanded]="expanded">
    <ng-container header>
        <p>Accordion Header</p>
    </ng-container>
    <ng-container content>
        <p>Accordion Content</p>
    </ng-container>
</aurelius-ui-accordion>
`;

export const Primary: Story = {
    args: {
        expanded: true,
    },
    render: (args) => ({
        props: args,
        template: primaryTemplate,
    }),
};

export const Collapsed: Story = {
    args: {
        expanded: false,
    },
    render: (args) => ({
        props: args,
        template: primaryTemplate,
    }),
};

export const Empty: Story = {
    args: {
        expanded: false,
    },
};
