module.exports = {
  name: 'permissions',
  preset: '../../jest.config.js',
  coverageDirectory: '../../coverage/libs/permissions',
  snapshotSerializers: [
    'jest-preset-angular/AngularSnapshotSerializer.js',
    'jest-preset-angular/HTMLCommentSerializer.js'
  ]
};
