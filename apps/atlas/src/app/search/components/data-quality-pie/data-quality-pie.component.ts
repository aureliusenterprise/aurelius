import { Component, ElementRef, HostBinding, Input } from '@angular/core';

@Component({
  selector: 'models4insight-data-quality-pie',
  templateUrl: 'data-quality-pie.component.html',
  styleUrls: ['data-quality-pie.component.scss']
})
export class DataQualityPieComponent {
  @Input() value: number;
  @Input() size: number = 4;

  @HostBinding('title')
  get title() {
    return `${this.value}%`;
  }
}
