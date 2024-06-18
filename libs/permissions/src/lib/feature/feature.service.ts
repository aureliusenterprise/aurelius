import { Injectable } from '@angular/core';
import { BasicStore, StoreService } from '@models4insight/redux';

export interface FeatureStoreContext {
  readonly subscription?: {
    readonly [featureName: string]: boolean;
  };
}

export enum Feature {
  ANALYTICS_ACCESS = 'analytics_access',
  DATA2MODEL_ACCESS = 'data2model_access',
  DATA2MODEL_BRANCH_CREATE = 'data2model_branch_create',
  DATA2MODEL_MODEL_SAVE = 'data2model_model_save',
  DATA2MODEL_RULES_EDIT = 'data2model_rules_edit',
  DATA2MODEL_RULES_SAVE = 'data2model_rules_save',
  DATA2MODEL_SUGGESTIONS = 'data2model_suggestions',
  PLATFORM_ACCESS = 'platform_access',
  PLATFORM_BRANCH_ACCESS_RIGHTS = 'platform_branch_access_rights',
  PLATFORM_BRANCH_CREATE = 'platform_branch_create',
  PLATFORM_BRANCH_MERGE = 'platform_branch_merge',
  PLATFORM_MODEL_EXPLORE = 'platform_model_explore',
  PLATFORM_MODEL_RETRIEVE = 'platform_model_retrieve',
  PLATFORM_MODEL_UPLOAD = 'platform_model_upload',
  PLATFORM_PROJECT_COLLABORATE = 'platform_project_collaborate',
  PLATFORM_PROJECT_CONTINUE_WORKING = 'platform_project_continue_working',
  PLATFORM_PROJECT_CREATE = 'platform_project_create',
  PLATFORM_PROJECT_HOME = 'platform_project_home',
  PLATFORM_USER_GROUPS_CREATE = 'platform_user_groups_create',
}

@Injectable()
export class FeatureService extends BasicStore<FeatureStoreContext> {
  constructor(storeService: StoreService) {
    super({ name: 'FeatureService', storeService });
  }

  /**
   * Checks with the backend whether or not the current user can access the feature with the given name and updates the store accordingly.
   */
  checkPermission(feature: Feature) {
    // This is a placeholder while the backend function is not yet available
    this.update({
      description: `Subscription updated for feature ${feature}`,
      path: ['subscription', feature],
      payload: true,
    });

    return this.select(['subscription', feature]);
  }
}
