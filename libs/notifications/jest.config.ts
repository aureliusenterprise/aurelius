export default {
    displayName: 'notifications',
    preset: '../../jest.preset.js',
    coverageDirectory: '../../coverage/libs/notifications',
    snapshotSerializers: [
        'jest-preset-angular/AngularSnapshotSerializer.js',
        'jest-preset-angular/HTMLCommentSerializer.js',
    ],
};
