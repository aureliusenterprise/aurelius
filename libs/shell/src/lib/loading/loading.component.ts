import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs';
import { ShellService } from '../shell.service';

@Component({
  selector: 'models4insight-loading',
  templateUrl: './loading.component.html',
  styleUrls: ['./loading.component.scss'],
})
export class LoadingComponent implements OnInit {
  isActive$: Observable<boolean>;

  constructor(private shellService: ShellService) {}

  ngOnInit() {
    this.isActive$ = this.shellService.select('isNavigating');
  }
}
