import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';
import { NgxPageScrollCoreModule } from 'ngx-page-scroll-core';
import { HeroComponent } from './hero.component';

@NgModule({
  imports: [CommonModule, NgxPageScrollCoreModule, RouterModule],
  declarations: [HeroComponent],
  exports: [HeroComponent],
})
export class HeroModule {}
