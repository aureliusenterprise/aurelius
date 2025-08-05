import type { Meta, StoryObj } from "@storybook/angular";
import { Card } from "./card.component";

const meta: Meta<Card> = {
    component: Card,
    title: "Card",
};
export default meta;

type Story = StoryObj<Card>;

const template = `
<aurelius-ui-card>
    <ng-container card-image>
    <figure class="image is-square">
      <img
        [attr.src]="image"
        alt="Card Image"
      />
    </figure>
    </ng-container>
    <ng-container card-content>
        <div class="media">
            <div class="media-content">
                <p class="title">{{ title }}</p>
                <p class="subtitle">{{ subtitle }}</p>
            </div>
        </div>
        <div class="content">
            <p>{{ content }}</p>
        </div>
    </ng-container>
    <ng-container card-footer>
        <button class="card-footer-item">{{ button1 }}</button>
        <button class="card-footer-item">{{ button2 }}</button>
    </ng-container>
</aurelius-ui-card>
`;

export const Primary: Story = {
    args: {
        image: "/assets/logo.jpg",
        title: "Title",
        subtitle: "This is a sample subtitle",
        content: "This is a sample card content.",
        button1: "Action",
        button2: "Other",
    },
    render: (args) => ({
        props: args,
        template,
    }),
};

export const Empty: Story = {};
