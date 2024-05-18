import { DOCUMENT } from '@angular/common';
import { Component, ElementRef, Inject, ViewChild } from '@angular/core';
import { faArrowAltCircleUp, faBars } from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'models4insight-details-navigation',
  templateUrl: 'details-navigation.component.html',
  styleUrls: ['details-navigation.component.scss']
})
export class DetailsNavigationComponent {
  readonly faBars = faBars;
  readonly faArrowAltCircleUp = faArrowAltCircleUp;

  @ViewChild('toggleButton') readonly toggleButton: ElementRef<
    HTMLButtonElement
  >;

  isActive = false;

  constructor(@Inject(DOCUMENT) readonly document: Document) {}

  toggleIsActive() {
    this.isActive = !this.isActive;
    this.toggleButton.nativeElement.blur();
  }
}
