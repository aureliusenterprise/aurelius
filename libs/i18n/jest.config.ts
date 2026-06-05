export default {
    displayName: 'i18n',
    preset: '../../jest.preset.js',
    coverageDirectory: '../../coverage/libs/i18n',
    snapshotSerializers: [
        'jest-preset-angular/AngularSnapshotSerializer.js',
        'jest-preset-angular/HTMLCommentSerializer.js',
    ],
};
