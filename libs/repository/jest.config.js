module.exports = {
  name: 'repository',
  preset: '../../jest.config.js',
  coverageDirectory: '../../coverage/libs/repository',
  snapshotSerializers: [
    'jest-preset-angular/AngularSnapshotSerializer.js',
    'jest-preset-angular/HTMLCommentSerializer.js'
  ]
};
