export default {
    displayName: 'consistency-metrics',
    preset: '../../jest.preset.js',
    coverageDirectory: '../../coverage/apps/consistency-metrics',
    snapshotSerializers: [
        'jest-preset-angular/build/serializers/no-ng-attributes',
        'jest-preset-angular/build/serializers/ng-snapshot',
        'jest-preset-angular/build/serializers/html-comment',
    ],
};
