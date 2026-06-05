export default {
    displayName: 'data2model',
    preset: '../../jest.preset.js',
    coverageDirectory: '../../coverage/apps/data2model',
    snapshotSerializers: [
        'jest-preset-angular/AngularSnapshotSerializer.js',
        'jest-preset-angular/HTMLCommentSerializer.js',
    ],
};
