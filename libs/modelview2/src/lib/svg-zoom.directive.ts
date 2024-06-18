import {
  AfterContentInit,
  ContentChildren,
  Directive,
  ElementRef,
  OnDestroy,
} from '@angular/core';
import { select, Selection } from 'd3-selection';
import { zoom, ZoomBehavior, zoomIdentity, ZoomTransform } from 'd3-zoom';

const zoomBehavior = zoom().scaleExtent([0.5, 3]);

@Directive({ selector: 'models4insight-svg-zoom, [models4insight-svg-zoom]' })
export class SVGZoomDirective implements AfterContentInit, OnDestroy {
  @ContentChildren('zoomTarget') zoomTargets: ElementRef<HTMLElement>[];

  private currentZoom: ZoomTransform = zoomIdentity;
  private zoomBehaviorInstance: ZoomBehavior<Element, unknown>;
  private zoomContainer: Selection<Element, unknown, Element, unknown>;

  constructor(private readonly elementRef: ElementRef<HTMLElement>) {}

  ngAfterContentInit() {
    this.zoomContainer = select(this.elementRef.nativeElement);
    this.zoomBehaviorInstance = zoomBehavior.on('zoom', ({ transform }) => {
      this.applyZoom(transform);
    });
    this.zoomContainer.call(this.zoomBehaviorInstance as any);
  }

  ngOnDestroy() {}

  resetZoom() {
    if (!this.zoomBehaviorInstance) return;
    const result = this.currentZoom;
    this.setZoom(zoomIdentity);
    return result;
  }

  setZoom(zoomTransform: ZoomTransform) {
    this.zoomBehaviorInstance.transform(
      this.zoomContainer as any,
      zoomTransform
    );
    this.applyZoom(zoomTransform);
  }

  private applyZoom(zoomTransform: ZoomTransform) {
    this.currentZoom = zoomTransform;
    for (const zoomTarget of this.zoomTargets) {
      zoomTarget.nativeElement.setAttribute(
        'transform',
        zoomTransform.toString()
      );
    }
  }
}
