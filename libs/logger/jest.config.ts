export default {
    displayName: 'logger',
    preset: '../../jest.preset.js',
    coverageDirectory: '../../coverage/libs/logger',
    snapshotSerializers: [
        'jest-preset-angular/AngularSnapshotSerializer.js',
        'jest-preset-angular/HTMLCommentSerializer.js',
    ],
};
