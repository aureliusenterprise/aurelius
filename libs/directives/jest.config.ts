export default {
    displayName: 'directives',
    preset: '../../jest.preset.js',
    coverageDirectory: '../../coverage/libs/directives',
    snapshotSerializers: [
        'jest-preset-angular/AngularSnapshotSerializer.js',
        'jest-preset-angular/HTMLCommentSerializer.js',
    ],
};
