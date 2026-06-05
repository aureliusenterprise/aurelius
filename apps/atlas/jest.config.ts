export default {
    displayName: 'atlas',
    preset: '../../jest.preset.js',
    coverageDirectory: '../../coverage/apps/atlas',
    snapshotSerializers: [
        'jest-preset-angular/AngularSnapshotSerializer.js',
        'jest-preset-angular/HTMLCommentSerializer.js',
    ],
};
