export default {
    displayName: 'redux',
    preset: '../../jest.preset.js',
    coverageDirectory: '../../coverage/libs/redux',
    snapshotSerializers: [
        'jest-preset-angular/AngularSnapshotSerializer.js',
        'jest-preset-angular/HTMLCommentSerializer.js',
    ],
};
