import { moduleMetadata } from '@storybook/angular';
import { Mermaid } from 'mdx-mermaid/Mermaid';
import { DomainsWizardComponent } from '../domains-wizard/domains-wizard.component';
import { DomainsWizardModule } from '../domains-wizard/domains-wizard.module';
import { SummaryWizardComponent } from '../summary-wizard/summary-wizard.component';
import { SummaryWizardModule } from '../summary-wizard/summary-wizard.module';
import { SystemsWizardComponent } from '../systems-wizard/systems-wizard.component';
import { SystemsWizardModule } from '../systems-wizard/systems-wizard.module';
import { WelcomeWizardComponent } from '../welcome-wizard/welcome-wizard.component';
import { WelcomeWizardModule } from '../welcome-wizard/welcome-wizard.module';

export default {
  title: 'Apps/Atlas/Mockups/Dashboards/First Time Setup',

  decorators: [
    moduleMetadata({
      imports: [
        DomainsWizardModule,
        SummaryWizardModule,
        SystemsWizardModule,
        WelcomeWizardModule,
      ],
    }),
  ],
};

export const Welcome = {
  render: () => ({
    component: WelcomeWizardComponent,
  }),

  name: 'Welcome',
  height: '575px',
};

export const DataDomains = {
  render: () => ({
    component: DomainsWizardComponent,
  }),

  name: 'Data domains',
  height: '800px',
};

export const Systems = {
  render: () => ({
    component: SystemsWizardComponent,
  }),

  name: 'Systems',
  height: '800px',
};

export const Summary = {
  render: () => ({
    component: SummaryWizardComponent,
  }),

  name: 'Summary',
  height: '888px',
};
