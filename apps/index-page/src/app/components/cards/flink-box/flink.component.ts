import { Component, OnInit } from '@angular/core';
import { faAngleDown } from '@fortawesome/free-solid-svg-icons';
@Component({
    selector: 'models4insight-flink',
    templateUrl: './flink.component.html',
    styleUrls: ['./flink.component.scss'],
})
export class FlinkComponent implements OnInit {
    readonly angleDown = faAngleDown;

    constructor() {}

    ngOnInit(): void {}
}
