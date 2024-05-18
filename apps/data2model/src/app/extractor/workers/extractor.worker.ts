/// <reference lib="webworker" />

import { Dictionary } from 'lodash';
import { ExtractorWorkerContext, ExtractorWorkerTask } from '../extractor-types';
import { bijacencyMap } from './bijacency-map';
import { suggestions } from './suggestions';

const tasks: Dictionary<(args: Dictionary<any>) => Promise<any>> = {
  [ExtractorWorkerTask.SUGGESTIONS]: suggestions,
  [ExtractorWorkerTask.BIJACENCY_MAP]: bijacencyMap
};

addEventListener(
  'message',
  async ({ data }: { data: ExtractorWorkerContext }) => {
    const task = tasks[data.task];

    if (!task) {
      throw new TypeError(`Operation ${data.task} is not supported!`);
    }

    postMessage(await task(data.context));
  }
);
