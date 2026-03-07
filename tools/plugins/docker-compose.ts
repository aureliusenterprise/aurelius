import { CreateNodesResult, CreateNodes } from '@nx/devkit';
import { existsSync } from 'fs';
import { dirname, join } from 'path';

export interface DockerComposePluginOptions {
    readonly serveTargetName?: string;
}

const glob = '**/docker-compose.{yml,yaml}';

export const createNodes: CreateNodes<DockerComposePluginOptions> = [
    glob,
    async (configFilePath, options) => {
        return createNodesInternal(configFilePath, options);
    },
];

async function createNodesInternal(
    configFilePath: string,
    { serveTargetName = 'serve' }: DockerComposePluginOptions = {},
): Promise<CreateNodesResult> {
    const projectRoot = dirname(configFilePath);

    // The docker-compose file must be in the same directory as the project.json file
    if (!existsSync(join(projectRoot, 'project.json'))) {
        return {};
    }

    return {
        projects: {
            [projectRoot]: {
                tags: ['docker-compose'],
                targets: {
                    [serveTargetName]: {
                        command: 'docker compose up',
                        dependsOn: [
                            { target: 'decrypt' },
                            { target: 'docker-build' },
                            { target: 'docker-build', dependencies: true },
                        ],
                        metadata: {
                            description: 'Run the service locally.',
                        },
                        options: {
                            cwd: projectRoot,
                        },
                    },
                },
            },
        },
    };
}
