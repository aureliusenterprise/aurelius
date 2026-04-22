import { createNodesFromFiles, CreateNodesResult, CreateNodesV2 } from "@nx/devkit";
import { dirname } from "path";

export interface DockerPluginOptions {
    readonly buildTargetName?: string;
    readonly publishTargetName?: string;
    readonly setupDockerBuilderTargetName?: string;
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
    {
        buildTargetName = "docker-build",
        publishTargetName = "docker-publish",
        setupDockerBuilderTargetName = "docker-setup-builder",
    }: DockerPluginOptions = {},
): Promise<CreateNodesResult> {
    const projectRoot = dirname(configFilePath);

    return {
        projects: {
            ["."]: {
                targets: {
                    [setupDockerBuilderTargetName]: {
                        command:
                            "docker buildx create --name {args.builder} --node {args.builder} --driver docker-container",
                        metadata: {
                            description: "Set up the Docker Buildx builder instance",
                        },
                        options: {
                            builder: "container",
                            env: {
                                DOCKER_BUILDKIT: "1",
                            },
                        },
                    },
                },
            },
            [projectRoot]: {
                tags: ["docker"],
                targets: {
                    [buildTargetName]: {
                        command: `docker buildx build . -f ${configFilePath} -t {args.namespace}/{projectName}:{args.version} --build-arg VERSION={args.version}`,
                        dependsOn: [{ target: "build" }, { target: buildTargetName, dependencies: true }],
                        metadata: {
                            description: "Build the Docker image for the application",
                        },
                        options: {
                            env: {
                                DOCKER_BUILDKIT: "1",
                            },
                            namespace: "ghcr.io/aureliusenterprise",
                            version: "local",
                        },
                    },
                    [publishTargetName]: {
                        command: `docker buildx build . -f ${configFilePath} -t {args.namespace}/{projectName}:{args.version} --build-arg VERSION={args.version} --builder {args.builder} --provenance=true --sbom=true --push`,
                        options: {
                            env: {
                                DOCKER_BUILDKIT: "1",
                            },
                            builder: "container",
                            namespace: "ghcr.io/aureliusenterprise",
                            version: "latest",
                        },
                        dependsOn: [
                            { target: "build" },
                            { target: setupDockerBuilderTargetName, projects: ["."], params: "forward" },
                            { target: publishTargetName, dependencies: true, params: "forward" },
                        ],
                        metadata: {
                            description: "Publish the Docker image for the application",
                        },
                    },
                },
            },
        },
    };
}
