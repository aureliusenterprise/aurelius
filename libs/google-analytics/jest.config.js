module.exports = {
  name: 'google-analytics',
  preset: '../../jest.config.js',
  coverageDirectory: '../../coverage/libs/google-analytics',
  snapshotSerializers: [
    'jest-preset-angular/AngularSnapshotSerializer.js',
    'jest-preset-angular/HTMLCommentSerializer.js'
  ]
};
