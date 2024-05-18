module.exports = {
  name: 'redux',
  preset: '../../jest.config.js',
  coverageDirectory: '../../coverage/libs/redux',
  snapshotSerializers: [
    'jest-preset-angular/AngularSnapshotSerializer.js',
    'jest-preset-angular/HTMLCommentSerializer.js'
  ]
};
