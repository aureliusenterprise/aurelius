export default {
    displayName: 'services-branch',
    preset: '../../../jest.preset.js',
    coverageDirectory: '../../../coverage/libs/services/branch',
    snapshotSerializers: [
        'jest-preset-angular/AngularSnapshotSerializer.js',
        'jest-preset-angular/HTMLCommentSerializer.js',
    ],
};
