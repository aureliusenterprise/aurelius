import { CreateNodes, CreateNodesResult } from '@nx/devkit';
import { execSync } from 'node:child_process';
import { dirname } from 'node:path';

export interface DockerPluginOptions {
    readonly attestTargetName?: string;
    readonly buildTargetName?: string;
    readonly licenseScanTargetName?: string;
    readonly publishTargetName?: string;
    readonly sbomTargetName?: string;
    readonly setupBuilderTargetName?: string;
    readonly signTargetName?: string;
    readonly verifyTargetName?: string;
    readonly vulnScanTargetName?: string;
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
    {
        attestTargetName = 'docker-attest',
        buildTargetName = 'docker-build',
        licenseScanTargetName = 'docker-license-scan',
        publishTargetName = 'docker-publish',
        sbomTargetName = 'docker-sbom',
        setupBuilderTargetName = 'docker-setup-builder',
        signTargetName = 'docker-sign',
        verifyTargetName = 'docker-verify',
        vulnScanTargetName = 'docker-vuln-scan',
    }: DockerPluginOptions = {},
): Promise<CreateNodesResult> {
    const projectRoot = dirname(configFilePath);
    const branchName = getBranchName();

    return {
        projects: {
            ['.']: {
                targets: {
                    [setupBuilderTargetName]: {
                        command:
                            'docker buildx create --name {args.builder} --node {args.builder} --driver docker-container',
                        metadata: {
                            description: 'Set up the Docker Buildx builder instance',
                        },
                        options: {
                            builder: 'container',
                            env: {
                                DOCKER_BUILDKIT: '1',
                            },
                        },
                    },
                },
            },
            [projectRoot]: {
                tags: ['docker'],
                targets: {
                    [attestTargetName]: {
                        command:
                            "DIGEST=$(docker buildx imagetools inspect {args.namespace}/{projectName}:{args.version} --format '{{.Manifest.Digest}}') && cosign attest --predicate {projectRoot}/sbom.json --type cyclonedx {args.namespace}/{projectName}@${DIGEST}",
                        dependsOn: [{ target: 'docker-sbom', params: 'forward' }],
                        options: {
                            namespace: 'ghcr.io/aureliusenterprise',
                            version: 'local',
                        },
                        metadata: {
                            description: 'Attest the Docker image using Cosign and the generated SBOM',
                        },
                    },
                    [buildTargetName]: {
                        command: `docker buildx build . -f ${configFilePath} -t {args.namespace}/{projectName}:{args.version} --build-arg VERSION={args.version} --cache-from="type=registry,ref={args.namespace}/{projectName}-cache:main" --cache-from="type=registry,ref={args.namespace}/{projectName}-cache:${branchName}" --cache-to="type=registry,ref={args.namespace}/{projectName}-cache:${branchName},mode=max"`,
                        dependsOn: [
                            { target: 'build' },
                            { target: setupBuilderTargetName, projects: ['.'], params: 'forward' },
                            { target: buildTargetName, dependencies: true },
                        ],
                        metadata: {
                            description: 'Build the Docker image for the application',
                        },
                        options: {
                            env: {
                                DOCKER_BUILDKIT: '1',
                            },
                            namespace: 'ghcr.io/aureliusenterprise',
                            version: 'local',
                        },
                    },
                    [publishTargetName]: {
                        command: `docker buildx build . -f ${configFilePath} -t {args.namespace}/{projectName}:{args.version} --build-arg VERSION={args.version} --builder {args.builder} --provenance=true --push --cache-from="type=registry,ref={args.namespace}/{projectName}-cache:main" --cache-from="type=registry,ref={args.namespace}/{projectName}-cache:${branchName}" --cache-to="type=registry,ref={args.namespace}/{projectName}-cache:${branchName},mode=max"`,
                        options: {
                            env: {
                                DOCKER_BUILDKIT: '1',
                            },
                            builder: 'container',
                            namespace: 'ghcr.io/aureliusenterprise',
                            version: 'latest',
                        },
                        dependsOn: [
                            { target: 'build' },
                            { target: setupBuilderTargetName, projects: ['.'], params: 'forward' },
                            { target: publishTargetName, dependencies: true, params: 'forward' },
                        ],
                        metadata: {
                            description: 'Publish the Docker image for the application',
                        },
                    },
                    [sbomTargetName]: {
                        executor: 'nx:run-commands',
                        options: {
                            command:
                                'trivy image --format cyclonedx --output {args.sbomPath} {args.namespace}/{projectName}:{args.version} --cache-dir {projectRoot}/.trivy-cache',
                            namespace: 'ghcr.io/aureliusenterprise',
                            sbomPath: '{projectRoot}/sbom.json',
                            version: 'local',
                        },
                        metadata: {
                            description: 'Generate a Software Bill of Materials (SBOM) for the Docker image',
                        },
                    },
                    [signTargetName]: {
                        command:
                            "DIGEST=$(docker buildx imagetools inspect {args.namespace}/{projectName}:{args.version} --format '{{.Manifest.Digest}}') && cosign sign --yes {args.namespace}/{projectName}@${DIGEST}",
                        options: {
                            namespace: 'ghcr.io/aureliusenterprise',
                            version: 'local',
                        },
                        metadata: {
                            description: 'Sign the Docker image with Cosign',
                        },
                    },
                    [verifyTargetName]: {
                        command:
                            "DIGEST=$(docker buildx imagetools inspect {args.namespace}/{projectName}:{args.version} --format '{{.Manifest.Digest}}') && cosign verify {args.namespace}/{projectName}@${DIGEST} --certificate-identity-regexp '{args.identity}' --certificate-oidc-issuer-regexp '{args.issuer}'",
                        options: {
                            identity: '.*',
                            issuer: '.*',
                            namespace: 'ghcr.io/aureliusenterprise',
                            version: 'local',
                        },
                        metadata: {
                            description: 'Verify Cosign signatures for the Docker image',
                        },
                    },
                    [licenseScanTargetName]: {
                        command:
                            'trivy sbom {args.sbomPath} --scanners license --format json --output {args.reportPath} --exit-code {args.exitCode} --cache-dir {projectRoot}/.trivy-cache',
                        dependsOn: [{ target: sbomTargetName, params: 'forward' }],
                        options: {
                            exitCode: 0,
                            reportPath: '{projectRoot}/licenses.json',
                            sbomPath: '{projectRoot}/sbom.json',
                        },
                        metadata: {
                            description: 'Scan the Docker image for license compliance using Trivy',
                        },
                    },
                    [vulnScanTargetName]: {
                        configurations: {
                            json: {
                                command:
                                    'trivy sbom {args.sbomPath} --scanners vuln --format json --output {args.reportPath} --exit-code {args.exitCode}',
                                exitCode: 0,
                                reportPath: '{projectRoot}/vulnerabilities.json',
                                sbomPath: '{projectRoot}/sbom.json',
                            },
                            sarif: {
                                command:
                                    'trivy sbom {args.sbomPath} --scanners vuln --format sarif --output {args.reportPath} --exit-code {args.exitCode}',
                                exitCode: 0,
                                reportPath: '{projectRoot}/vulnerabilities.sarif',
                                sbomPath: '{projectRoot}/sbom.json',
                            },
                        },
                        defaultConfiguration: 'json',
                        dependsOn: [{ target: sbomTargetName, params: 'forward' }],
                        executor: 'nx:run-commands',
                        options: {
                            exitCode: 0,
                            reportPath: '{projectRoot}/vulnerabilities.json',
                            sbomPath: '{projectRoot}/sbom.json',
                        },
                        metadata: {
                            description: 'Scan the Docker image for vulnerabilities using Trivy',
                        },
                    },
                },
            },
        },
    };
}
