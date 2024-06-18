import { NgModule } from '@angular/core';
import { IntersectionObserverDirective } from './intersection-observer.directive';

@NgModule({
  declarations: [IntersectionObserverDirective],
  exports: [IntersectionObserverDirective],
})
export class IntersectionObserverModule {}
