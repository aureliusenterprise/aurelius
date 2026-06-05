export default {
    displayName: 'shell',
    preset: '../../jest.preset.js',
    coverageDirectory: '../../coverage/libs/shell',
    snapshotSerializers: [
        'jest-preset-angular/AngularSnapshotSerializer.js',
        'jest-preset-angular/HTMLCommentSerializer.js',
    ],
};
