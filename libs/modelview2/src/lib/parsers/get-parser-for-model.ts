import { Dictionary } from 'lodash';
import { parseModel as parseArchimate3Model } from './archimate3';
import { ModelParserFunction } from './types';

const parsersByPrefix: Dictionary<ModelParserFunction> = {
  ar3: parseArchimate3Model,
};

function getPrefix(key: string) {
  return key?.split('_')[0];
}

export function getParserForModel(jsonModel: any): ModelParserFunction {
  // Get the prefix of the first key in the model to determine the format
  const prefix = getPrefix(Object.keys(jsonModel)[0]);

  const parser = parsersByPrefix[prefix];

  if (parser === null || parser === undefined) {
    throw Error(`No parser found for prefix ${prefix}`);
  }

  return parser;
}
