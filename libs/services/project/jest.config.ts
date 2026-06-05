export default {
    displayName: 'services-project',
    preset: '../../../jest.preset.js',
    coverageDirectory: '../../../coverage/libs/services/project',
    snapshotSerializers: [
        'jest-preset-angular/AngularSnapshotSerializer.js',
        'jest-preset-angular/HTMLCommentSerializer.js',
    ],
};
