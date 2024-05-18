module.exports = {
  name: 'services-project',
  preset: '../../../jest.config.js',
  coverageDirectory: '../../../coverage/libs/services/project',
  snapshotSerializers: [
    'jest-preset-angular/AngularSnapshotSerializer.js',
    'jest-preset-angular/HTMLCommentSerializer.js'
  ]
};
