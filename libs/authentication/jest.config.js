module.exports = {
  name: 'authentication',
  preset: '../../jest.config.js',
  coverageDirectory: '../../coverage/libs/authentication',
  snapshotSerializers: [
    'jest-preset-angular/AngularSnapshotSerializer.js',
    'jest-preset-angular/HTMLCommentSerializer.js'
  ]
};
