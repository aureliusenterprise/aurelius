import { Directive, ElementRef, Input, OnDestroy } from '@angular/core';

declare var Bokeh;

@Directive({
  exportAs: 'models4insight-bokeh-chart',
  selector: 'models4insight-bokeh-chart, [models4insight-bokeh-chart]',
})
export class BokehChartDirective implements OnDestroy {
  @Input() id: string;

  constructor(private readonly elementRef: ElementRef) {}

  ngOnDestroy() {
    this.clear();
  }

  @Input()
  set chart(json: any) {
    // First, clear any previous chart.
    this.clear();
    // Then, draw the new chart
    if (json) {
      Bokeh.embed.embed_item(json, this.id);
    }
  }

  private clear() {
    const { nativeElement } = this.elementRef;
    while (nativeElement.hasChildNodes()) {
      nativeElement.removeChild(nativeElement.lastChild);
    }
    nativeElement.removeAttribute('style');
  }
}
