import { InjectionToken } from '@angular/core';

export interface ProjectServiceConfig {
  readonly standalone: boolean;
}

export const ProjectServiceConfig = new InjectionToken<ProjectServiceConfig>(
  'ProjectServiceConfig'
);
