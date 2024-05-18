import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { IntersectionObserverModule } from '@models4insight/directives';
import { InfiniteScrollContainerComponent } from './infinite-scroll-container.component';

@NgModule({
  imports: [CommonModule, IntersectionObserverModule],
  declarations: [InfiniteScrollContainerComponent],
  exports: [InfiniteScrollContainerComponent],
})
export class InfiniteScrollContainerModule {}
