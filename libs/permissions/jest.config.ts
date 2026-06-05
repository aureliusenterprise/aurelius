export default {
    displayName: 'permissions',
    preset: '../../jest.preset.js',
    coverageDirectory: '../../coverage/libs/permissions',
    snapshotSerializers: [
        'jest-preset-angular/AngularSnapshotSerializer.js',
        'jest-preset-angular/HTMLCommentSerializer.js',
    ],
};
