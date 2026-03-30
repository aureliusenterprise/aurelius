import { CreateNodes, CreateNodesResult } from '@nx/devkit';
import { dirname } from 'path';
import { execSync } from 'child_process';

export interface DockerPluginOptions {
    readonly buildTargetName?: string;
    readonly publishTargetName?: string;
}

const glob = '**/Dockerfile';

export const createNodes: CreateNodes<DockerPluginOptions> = [
    glob,
    async (configFilePath, options) => {
        return createNodesInternal(configFilePath, options);
    },
];

function getBranchName(): string {
    const branchName = process.env.GITHUB_REF_NAME || execSync('git rev-parse --abbrev-ref HEAD').toString().trim();
    return branchName.replace(/\//g, '-');
}

async function createNodesInternal(
    configFilePath: string,
    { buildTargetName = 'docker-build', publishTargetName = 'docker-publish' }: DockerPluginOptions = {},
): Promise<CreateNodesResult> {
    const projectRoot = dirname(configFilePath);
    const branchName = getBranchName();

    return {
        projects: {
            [projectRoot]: {
                tags: ['docker'],
                targets: {
                    [buildTargetName]: {
                        command: `docker buildx build . -f ${configFilePath} -t {projectName}:local --cache-from="type=registry,ref={args.namespace}/{projectName}-cache:main" --cache-from="type=registry,ref={args.namespace}/{projectName}-cache:${branchName}" --cache-to="type=registry,ref={args.namespace}/{projectName}-cache:${branchName},mode=max"`,
                        dependsOn: [{ target: 'build' }, { target: buildTargetName, dependencies: true }],
                        metadata: {
                            description: 'Build the Docker image for the application',
                        },
                        options: {
                            env: {
                                DOCKER_BUILDKIT: '1',
                            },
                            namespace: 'ghcr.io/aureliusenterprise',
                        },
                    },
                    [publishTargetName]: {
                        command: `docker buildx build . -f ${configFilePath} -t {args.namespace}/{projectName}:{args.version} --push --cache-from="type=registry,ref={args.namespace}/{projectName}-cache:main" --cache-from="type=registry,ref={args.namespace}/{projectName}-cache:${branchName}" --cache-to="type=registry,ref={args.namespace}/{projectName}-cache:${branchName},mode=max"`,
                        dependsOn: [{ target: 'build' }, { target: buildTargetName, dependencies: true }],
                        metadata: {
                            description: 'Publish the Docker image for the application',
                        },
                        options: {
                            env: {
                                DOCKER_BUILDKIT: '1',
                            },
                            namespace: 'ghcr.io/aureliusenterprise',
                            version: 'latest',
                        },
                    },
                },
            },
        },
    };
}
