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
    { buildTargetName = "docker-build", publishTargetName = "docker-publish" }: DockerPluginOptions = {},
): Promise<CreateNodesResult> {
    const projectRoot = dirname(configFilePath);

    return {
        projects: {
            [projectRoot]: {
                tags: ["docker"],
                targets: {
                    [buildTargetName]: {
                        command: `docker buildx build . -f ${configFilePath} -t {projectName}:local`,
                        dependsOn: [{ target: "build" }, { target: buildTargetName, dependencies: true }],
                        metadata: {
                            description: "Build the Docker image for the application",
                        },
                        options: {
                            env: {
                                DOCKER_BUILDKIT: "1",
                            },
                        },
                    },
                    [publishTargetName]: {
                        command: `docker buildx build . -f ${configFilePath} -t {args.namespace}/{projectName}:{args.version} --provenance=true --sbom=true --push`,
                        dependsOn: [{ target: "build" }, { target: buildTargetName, dependencies: true }],
                        metadata: {
                            description: "Publish the Docker image for the application",
                        },
                        options: {
                            env: {
                                DOCKER_BUILDKIT: "1",
                            },
                            namespace: "ghcr.io/aureliusenterprise",
                            version: "latest",
                        },
                    },
                },
            },
        },
    };
}
