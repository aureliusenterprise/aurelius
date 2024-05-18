module.exports = {
  name: 'i18n',
  preset: '../../jest.config.js',
  coverageDirectory: '../../coverage/libs/i18n',
  snapshotSerializers: [
    'jest-preset-angular/AngularSnapshotSerializer.js',
    'jest-preset-angular/HTMLCommentSerializer.js'
  ]
};
