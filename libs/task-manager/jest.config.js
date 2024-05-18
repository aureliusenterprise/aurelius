module.exports = {
  name: 'task-manager',
  preset: '../../jest.config.js',
  coverageDirectory: '../../coverage/libs/task-manager',
  snapshotSerializers: [
    'jest-preset-angular/AngularSnapshotSerializer.js',
    'jest-preset-angular/HTMLCommentSerializer.js'
  ]
};
