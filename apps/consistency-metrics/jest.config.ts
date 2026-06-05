export default {
    displayName: 'consistency-metrics',
    preset: '../../jest.preset.js',
    coverageDirectory: '../../coverage/apps/consistency-metrics',
    snapshotSerializers: [
        'jest-preset-angular/AngularSnapshotSerializer.js',
        'jest-preset-angular/HTMLCommentSerializer.js',
    ],
};
