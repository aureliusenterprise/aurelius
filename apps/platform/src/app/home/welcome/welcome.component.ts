import { Component } from '@angular/core';
import { faChartBar, faEye, faFlask, faProjectDiagram, IconDefinition } from '@fortawesome/free-solid-svg-icons';

interface CategoryContext {
  iconClass: IconDefinition;
  iconColor: string;
  title: string;
  description: string;
  redirectPath?: string;
}

@Component({
  selector: 'models4insight-welcome',
  templateUrl: 'welcome.component.html',
  styleUrls: ['welcome.component.scss']
})
export class WelcomeComponent {
  readonly insightsCategoryContext: CategoryContext = {
    iconClass: faChartBar,
    iconColor: 'has-text-primary',
    title: 'Insights',
    description: "I'm a decision maker",
    redirectPath: '/home/insights'
  };
  readonly modelingCategoryContext: CategoryContext = {
    iconClass: faProjectDiagram,
    iconColor: 'has-text-link',
    title: 'Modeling',
    description: 'I build models',
    redirectPath: '/home/modeling'
  };
  readonly analyticsCategoryContext: CategoryContext = {
    iconClass: faFlask,
    iconColor: 'has-text-success',
    title: 'Analytics',
    description: 'I make analyses using models'
    //redirectPath: '/home/analytics'
  };
  readonly monitoringCategoryContext: CategoryContext = {
    iconClass: faEye,
    iconColor: 'has-text-info',
    title: 'Monitoring',
    description: "I'm responsible for process quality"
    //redirectPath: '/home/monitoring'
  };
}
