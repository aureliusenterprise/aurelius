export default {
    displayName: 'services-model',
    preset: '../../../jest.preset.js',
    coverageDirectory: '../../../coverage/libs/services/model',
    snapshotSerializers: [
        'jest-preset-angular/AngularSnapshotSerializer.js',
        'jest-preset-angular/HTMLCommentSerializer.js',
    ],
};
