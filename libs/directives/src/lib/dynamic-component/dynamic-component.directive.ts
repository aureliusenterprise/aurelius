import {
  Component,
  ComponentFactoryResolver,
  Directive,
  Input,
  ViewContainerRef,
} from '@angular/core';

@Directive({
  selector:
    'models4insight-dynamic-component, [models4insight-dynamic-component]',
})
export class DynamicComponentDirective<T = Component> {
  private _instance: T;

  constructor(
    private readonly componentFactoryResolver: ComponentFactoryResolver,
    private readonly viewContainerRef: ViewContainerRef
  ) {}

  @Input('models4insight-dynamic-component') set component(
    component: new () => T
  ) {
    this.viewContainerRef.clear();

    if (component) {
      const componentFactory =
        this.componentFactoryResolver.resolveComponentFactory(component);

      const componentRef =
        this.viewContainerRef.createComponent(componentFactory);

      this._instance = componentRef.instance;
    }
  }

  get instance() {
    return this._instance;
  }
}
