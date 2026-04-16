import type { Meta, StoryObj } from "@storybook/angular";
import { Pagination } from "./pagination.component";

type ListItem = {
    id: number;
    name: string;
    role: string;
    handle: string;
    description: string;
};

const demoItems: ListItem[] = [
    {
        id: 1,
        name: "Ari",
        role: "Admin",
        handle: "@ari",
        description: "Manages platform settings and user permissions.",
    },
    {
        id: 2,
        name: "Bela",
        role: "Editor",
        handle: "@bela",
        description: "Creates and publishes content for the main blog.",
    },
    { id: 3, name: "Cora", role: "Viewer", handle: "@cora", description: "Reads published reports and dashboards." },
    {
        id: 4,
        name: "Dane",
        role: "Editor",
        handle: "@dane",
        description: "Drafts technical documentation and release notes.",
    },
    { id: 5, name: "Eli", role: "Admin", handle: "@eli", description: "Oversees integrations and third-party access." },
    { id: 6, name: "Faye", role: "Viewer", handle: "@faye", description: "Monitors analytics and usage statistics." },
    { id: 7, name: "Gio", role: "Editor", handle: "@gio", description: "Contributes to the product changelog." },
    { id: 8, name: "Hana", role: "Viewer", handle: "@hana", description: "Reviews shared assets and design exports." },
    { id: 9, name: "Ivan", role: "Admin", handle: "@ivan", description: "Configures deployment pipelines." },
    { id: 10, name: "Juno", role: "Editor", handle: "@juno", description: "Writes onboarding guides for new users." },
    { id: 11, name: "Kira", role: "Viewer", handle: "@kira", description: "Browses the public knowledge base." },
    {
        id: 12,
        name: "Luca",
        role: "Admin",
        handle: "@luca",
        description: "Handles billing and subscription management.",
    },
];

const meta: Meta<Pagination<ListItem>> = {
    component: Pagination,
    title: "Pagination",
};

export default meta;

type Story = StoryObj<Pagination<ListItem>>;

const mediaTemplate = `
<aurelius-ui-pagination [items]="items" [pageSize]="pageSize" [(pageIndex)]="pageIndex">
	<ng-template let-page>
        @for (item of page; track item.id) {
            <article class="media">
                <div class="media-content">
                    <div class="content">
                        <p>
                            <strong>{{ item.name }}</strong>
                            <br/>
                            <small>{{ item.handle }}&nbsp;–&nbsp;{{ item.role }}</small>
                            <br />
                            {{ item.description }}
                        </p>
                    </div>
                </div>
            </article>
        }
	</ng-template>
</aurelius-ui-pagination>
`;

export const Primary: Story = {
    args: {
        items: demoItems,
        pageSize: 4,
        pageIndex: 0,
    },
    render: (args) => ({
        props: args,
        template: mediaTemplate,
    }),
};

export const SecondPage: Story = {
    args: {
        items: demoItems,
        pageSize: 4,
        pageIndex: 1,
    },
    render: (args) => ({
        props: args,
        template: mediaTemplate,
    }),
};

export const Empty: Story = {
    args: {
        items: [],
        pageSize: 4,
        pageIndex: 0,
    },
    render: (args) => ({
        props: args,
        template: mediaTemplate,
    }),
};
