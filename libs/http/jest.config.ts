export default {
    displayName: 'http',
    preset: '../../jest.preset.js',
    coverageDirectory: '../../coverage/libs/http',
    snapshotSerializers: [
        'jest-preset-angular/AngularSnapshotSerializer.js',
        'jest-preset-angular/HTMLCommentSerializer.js',
    ],
};
