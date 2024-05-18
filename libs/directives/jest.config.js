module.exports = {
  name: 'directives',
  preset: '../../jest.config.js',
  coverageDirectory: '../../coverage/libs/directives',
  snapshotSerializers: [
    'jest-preset-angular/AngularSnapshotSerializer.js',
    'jest-preset-angular/HTMLCommentSerializer.js'
  ]
};
