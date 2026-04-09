import { createNodesFromFiles, CreateNodesResult, CreateNodesV2 } from "@nx/devkit";
import { dirname } from "path";

export interface SonarQubePluginOptions {
    readonly sonarTargetName?: string;
}

const glob = "**/sonar-project.properties";

export const createNodesV2: CreateNodesV2<SonarQubePluginOptions> = [
    glob,
    async (configFiles, options, context) => {
        return await createNodesFromFiles(
            (configFile) => createNodesInternal(configFile, options),
            configFiles,
            options,
            context,
        );
    },
];

async function createNodesInternal(
    configFilePath: string,
    { sonarTargetName = "sonar" }: SonarQubePluginOptions = {},
): Promise<CreateNodesResult> {
    const projectRoot = dirname(configFilePath);

    return {
        projects: {
            [projectRoot]: {
                targets: {
                    [sonarTargetName]: {
                        cache: true,
                        dependsOn: ["build", "decrypt"],
                        executor: "@nxlv/python:run-commands",
                        metadata: {
                            description: "Run SonarQube analysis on the project",
                        },
                        options: {
                            command: `sonar-scanner -Dproject.settings=${projectRoot}/sonar-project.properties -Dsonar.working.directory=${projectRoot}/.scannerwork`,
                            cwd: "{workspaceRoot}",
                        },
                        parallelism: false,
                    },
                },
            },
        },
    };
}
