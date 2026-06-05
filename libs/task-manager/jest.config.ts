export default {
    displayName: 'task-manager',
    preset: '../../jest.preset.js',
    coverageDirectory: '../../coverage/libs/task-manager',
    snapshotSerializers: [
        'jest-preset-angular/AngularSnapshotSerializer.js',
        'jest-preset-angular/HTMLCommentSerializer.js',
    ],
};
