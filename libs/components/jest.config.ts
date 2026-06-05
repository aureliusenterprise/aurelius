export default {
    displayName: 'components',
    preset: '../../jest.preset.js',
    coverageDirectory: '../../coverage/libs/components',
    snapshotSerializers: [
        'jest-preset-angular/AngularSnapshotSerializer.js',
        'jest-preset-angular/HTMLCommentSerializer.js',
    ],
};
