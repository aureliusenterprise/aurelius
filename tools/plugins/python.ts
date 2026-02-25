import { CreateNodesResult, CreateNodes, ProjectConfiguration, readJsonFile, TargetConfiguration } from '@nx/devkit';
import { existsSync } from 'fs';
import { basename, dirname, join } from 'path';

export interface PythonPluginOptions {
    readonly buildTargetName?: string;
    readonly e2ePath?: string;
    readonly e2eTargetName?: string;
    readonly lintTargetName?: string;
    readonly testPath?: string;
    readonly testTargetName?: string;
    readonly typecheckTargetName?: string;
}

const glob = '**/pyproject.toml';

export const createNodes: CreateNodes<PythonPluginOptions> = [
    glob,
    async (configFilePath, options) => {
        return createNodesInternal(configFilePath, options);
    },
];

function buildTargets(
    projectRoot: string,
    {
        buildTargetName = 'build',
        e2ePath = 'e2e',
        e2eTargetName = 'e2e',
        lintTargetName = 'lint',
        testPath = 'tests',
        testTargetName = 'test',
        typecheckTargetName = 'typecheck',
    }: PythonPluginOptions = {},
): Record<string, TargetConfiguration> {
    const targets: Record<string, TargetConfiguration> = {};

    if (!existsSync(join(projectRoot, 'project.json'))) {
        return targets;
    }

    targets[typecheckTargetName] = {
        cache: true,
        executor: '@nxlv/python:run-commands',
        metadata: {
            description: 'Run type checking on the Python code',
        },
        options: {
            command: `uv run pyright ${projectRoot}`,
        },
    };

    if (existsSync(join(projectRoot, e2ePath))) {
        targets[e2eTargetName] = {
            cache: true,
            dependsOn: [
                {
                    target: 'decrypt',
                },
                {
                    target: 'docker-build',
                },
            ],
            executor: '@nxlv/python:run-commands',
            metadata: {
                description: 'Run the end-to-end tests for this application',
            },
            options: {
                command: `uv run pytest ${e2ePath}`,
                cwd: projectRoot,
            },
        };
    }

    const projectJson = readJsonFile<ProjectConfiguration>(join(projectRoot, 'project.json'));

    if (!projectJson.sourceRoot) {
        return targets;
    }

    const moduleName = basename(projectJson.sourceRoot);

    if (!existsSync(join(projectRoot, moduleName))) {
        return targets;
    }

    targets[buildTargetName] = {
        cache: true,
        executor: '@nxlv/python:build',
        metadata: {
            description: 'Builds the Python package',
        },
        options: {
            bundleLocalDependencies: true,
            lockedVersions: false,
            outputPath: `${projectRoot}/dist/`,
            publish: false,
        },
        outputs: ['{projectRoot}/dist/'],
    };

    targets[lintTargetName] = {
        cache: true,
        executor: '@nxlv/python:ruff-check',
        metadata: {
            description: 'Lint the Python code',
        },
        options: {
            lintFilePatterns: [moduleName, testPath, e2ePath],
        },
    };

    if (existsSync(join(projectRoot, testPath))) {
        targets[testTargetName] = {
            cache: true,
            dependsOn: [
                {
                    target: 'decrypt',
                },
            ],
            executor: '@nxlv/python:run-commands',
            configurations: {
                ci: {
                    'cov-report': 'xml:coverage.xml',
                    cov: moduleName,
                },
            },
            metadata: {
                description: 'Run the unit tests for this application',
            },
            options: {
                command: `uv run pytest ${testPath}`,
                cwd: projectRoot,
            },
        };
    }

    return targets;
}

async function createNodesInternal(
    configFilePath: string,
    options: PythonPluginOptions | undefined,
): Promise<CreateNodesResult> {
    const projectRoot = dirname(configFilePath);

    const targets = buildTargets(projectRoot, options);

    return {
        projects: {
            [projectRoot]: {
                tags: ['python'],
                targets,
            },
        },
    };
}
