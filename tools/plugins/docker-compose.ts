import { createNodesFromFiles, CreateNodesResult, CreateNodesV2 } from "@nx/devkit";
import { existsSync } from "fs";
import { dirname, join } from "path";

export interface DockerComposePluginOptions {
    readonly serveTargetName?: string;
}

const glob = "**/docker-compose.{yml,yaml}";

export const createNodesV2: CreateNodesV2<DockerComposePluginOptions> = [
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
    { serveTargetName = "serve" }: DockerComposePluginOptions = {},
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
                        ],
                        metadata: {
                            description: "Run the service locally.",
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
