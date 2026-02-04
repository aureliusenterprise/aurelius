import { createNodesFromFiles, CreateNodesResult, CreateNodesV2 } from "@nx/devkit";
import { dirname } from "path";

export interface DockerPluginOptions {
    readonly buildTargetName?: string;
    readonly publishTargetName?: string;
}

const glob = "**/Dockerfile";

export const createNodesV2: CreateNodesV2<DockerPluginOptions> = [
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
    { buildTargetName = "docker-build" }: DockerPluginOptions = {},
): Promise<CreateNodesResult> {
    const projectRoot = dirname(configFilePath);

    return {
        projects: {
            [projectRoot]: {
                tags: ["docker"],
                targets: {
                    [buildTargetName]: {
                        command: `docker buildx build . -f ${configFilePath} -o {args.output} -t {args.namespace}/{args.tag}:{args.version}`,
                        configurations: {
                            local: {
                                output: "type=image",
                            },
                            publish: {
                                output: "type=registry,unpack=false",
                            },
                        },
                        defaultConfiguration: "local",
                        dependsOn: [{ target: "build" }, { target: buildTargetName, dependencies: true }],
                        metadata: {
                            description: "Build the Docker image for the application",
                        },
                        options: {
                            env: {
                                DOCKER_BUILDKIT: "1",
                            },
                            namespace: "ghcr.io/aureliusenterprise",
                            tag: "{projectName}",
                            version: "latest",
                        },
                    },
                },
            },
        },
    };
}
