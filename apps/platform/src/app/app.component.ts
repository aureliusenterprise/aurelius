import { Component } from '@angular/core';
import { Logger } from '@models4insight/logger';

const log = new Logger('App');

@Component({
  selector: 'models4insight-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {}
