export default {
    displayName: 'version',
    preset: '../../jest.preset.js',
    coverageDirectory: '../../coverage/libs/version',
    snapshotSerializers: [
        'jest-preset-angular/AngularSnapshotSerializer.js',
        'jest-preset-angular/HTMLCommentSerializer.js',
    ],
};
