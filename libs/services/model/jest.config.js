module.exports = {
  name: 'services-model',
  preset: '../../../jest.config.js',
  coverageDirectory: '../../../coverage/libs/services/model',
  snapshotSerializers: [
    'jest-preset-angular/AngularSnapshotSerializer.js',
    'jest-preset-angular/HTMLCommentSerializer.js'
  ]
};
