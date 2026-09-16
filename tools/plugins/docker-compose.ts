import { createNodesFromFiles, CreateNodesResult, CreateNodes } from "@nx/devkit";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";

export interface DockerComposePluginOptions {
    readonly serveTargetName?: string;
    readonly upTargetName?: string;
}

const glob = "**/docker-compose.{yml,yaml}";

export const createNodes: CreateNodes<DockerComposePluginOptions> = [
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
    { serveTargetName = "serve", upTargetName = "up" }: DockerComposePluginOptions = {},
): Promise<CreateNodesResult> {
    const projectRoot = dirname(configFilePath);

    // The docker-compose file must be in the same directory as the project.json file
    if (!existsSync(join(projectRoot, "project.json"))) {
        return {};
    }

    return {
        projects: {
            [projectRoot]: {
                tags: ["docker-compose"],
                targets: {
                    [serveTargetName]: {
                        continuous: true,
                        command: "docker compose up",
                        dependsOn: [
                            { target: "decrypt" },
                            { target: "docker-build" },
                            { target: "docker-build", dependencies: true },
                            { target: serveTargetName, dependencies: true },
                        ],
                        metadata: {
                            description: "Run the service locally.",
                        },
                        options: {
                            cwd: projectRoot,
                        },
                    },
                    [upTargetName]: {
                        command: "docker compose up -d --wait",
                        dependsOn: [
                            { target: "decrypt" },
                            { target: "docker-build" },
                            { target: "docker-build", dependencies: true },
                            { target: upTargetName, dependencies: true },
                        ],
                        metadata: {
                            description: "Start the service in the background and wait for it to become healthy.",
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
