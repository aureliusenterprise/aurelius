module.exports = {
  name: 'services-user-info',
  preset: '../../../jest.config.js',
  coverageDirectory: '../../../coverage/libs/services/user-info',
  snapshotSerializers: [
    'jest-preset-angular/AngularSnapshotSerializer.js',
    'jest-preset-angular/HTMLCommentSerializer.js'
  ]
};
