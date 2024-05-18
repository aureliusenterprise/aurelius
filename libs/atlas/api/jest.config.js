module.exports = {
  name: 'atlas-api',
  preset: '../../../jest.config.js',
  coverageDirectory: '../../../coverage/libs/atlas/api',
  snapshotSerializers: [
    'jest-preset-angular/AngularSnapshotSerializer.js',
    'jest-preset-angular/HTMLCommentSerializer.js'
  ]
};
