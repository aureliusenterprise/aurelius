export default {
    displayName: 'services-user-info',
    preset: '../../../jest.preset.js',
    coverageDirectory: '../../../coverage/libs/services/user-info',
    snapshotSerializers: [
        'jest-preset-angular/AngularSnapshotSerializer.js',
        'jest-preset-angular/HTMLCommentSerializer.js',
    ],
};
