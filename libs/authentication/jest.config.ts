export default {
    displayName: 'authentication',
    preset: '../../jest.preset.js',
    coverageDirectory: '../../coverage/libs/authentication',
    snapshotSerializers: [
        'jest-preset-angular/AngularSnapshotSerializer.js',
        'jest-preset-angular/HTMLCommentSerializer.js',
    ],
};
