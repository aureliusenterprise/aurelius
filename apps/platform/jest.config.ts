export default {
    displayName: 'platform',
    preset: '../../jest.preset.js',
    coverageDirectory: '../../coverage/apps/platform',
    snapshotSerializers: [
        'jest-preset-angular/AngularSnapshotSerializer.js',
        'jest-preset-angular/HTMLCommentSerializer.js',
    ],
};
