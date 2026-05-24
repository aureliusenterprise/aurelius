import { CreateNodes, CreateNodesResult } from '@nx/devkit';
import { dirname } from 'node:path';

export interface SonarQubePluginOptions {
    readonly sonarTargetName?: string;
}

const glob = '**/sonar-project.properties';

export const createNodes: CreateNodes<SonarQubePluginOptions> = [
    glob,
    async (configFilePath, options) => {
        return createNodesInternal(configFilePath, options);
    },
];

async function createNodesInternal(
    configFilePath: string,
    { sonarTargetName = 'sonar' }: SonarQubePluginOptions = {},
): Promise<CreateNodesResult> {
    const projectRoot = dirname(configFilePath);

    return {
        projects: {
            [projectRoot]: {
                tags: ['sonarqube'],
                targets: {
                    [sonarTargetName]: {
                        dependsOn: ['decrypt'],
                        executor: 'nx:run-commands',
                        metadata: {
                            description: 'Run SonarQube analysis on the project',
                        },
                        options: {
                            command: `sonar-scanner -Dproject.settings=${projectRoot}/sonar-project.properties -Dsonar.working.directory=${projectRoot}/.scannerwork`,
                        },
                    },
                },
            },
        },
    };
}
