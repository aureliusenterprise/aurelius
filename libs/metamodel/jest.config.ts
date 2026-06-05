export default {
    displayName: 'metamodel',
    preset: '../../jest.preset.js',
    coverageDirectory: '../../coverage/libs/metamodel',
    snapshotSerializers: [
        'jest-preset-angular/AngularSnapshotSerializer.js',
        'jest-preset-angular/HTMLCommentSerializer.js',
    ],
};
