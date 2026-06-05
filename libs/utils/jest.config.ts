export default {
    displayName: 'utils',
    preset: '../../jest.preset.js',
    coverageDirectory: '../../coverage/libs/utils',
    snapshotSerializers: [
        'jest-preset-angular/AngularSnapshotSerializer.js',
        'jest-preset-angular/HTMLCommentSerializer.js',
    ],
};
