module.exports = {
  name: 'services-branch',
  preset: '../../../jest.config.js',
  coverageDirectory: '../../../coverage/libs/services/branch',
  snapshotSerializers: [
    'jest-preset-angular/AngularSnapshotSerializer.js',
    'jest-preset-angular/HTMLCommentSerializer.js'
  ]
};
