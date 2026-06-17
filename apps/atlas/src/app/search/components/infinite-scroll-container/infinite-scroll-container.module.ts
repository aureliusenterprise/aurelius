import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { IntersectionObserverModule } from '@models4insight/directives';
import { InfiniteScrollContainerComponent } from './infinite-scroll-container.component';
import { TranslateModule } from '@ngx-translate/core';

@NgModule({
    imports: [CommonModule, IntersectionObserverModule, TranslateModule.forChild()],
    declarations: [InfiniteScrollContainerComponent],
    exports: [InfiniteScrollContainerComponent],
})
export class InfiniteScrollContainerModule {}
