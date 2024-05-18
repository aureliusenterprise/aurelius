import { Component, Input } from '@angular/core';
import { Router } from '@angular/router';
import { DomainForDashboard } from '@models4insight/atlas/api';

@Component({
  selector: 'models4insight-cards-dashboard',
  templateUrl: './cards-dashboard.component.html',
  styleUrls: ['./cards-dashboard.component.scss'],
  providers: []
})
export class CardDashboardComponent {
  constructor(private readonly router: Router) {}
  @Input() dataDomain: DomainForDashboard;

  directToDetailsPage(guid: string) {
    this.router.navigate(['search/details', guid]);
  }
}
