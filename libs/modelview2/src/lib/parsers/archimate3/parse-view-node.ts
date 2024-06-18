import { decodeXML, rgbToHex } from '@models4insight/utils';
import { ModelViewNode } from '../types';

const humanReadableTypes = {
  ar3_ArchiDiagramModelReference: 'View Reference',
  ar3_Container: 'Group',
  ar3_Label: 'Note',
};
const textAlignment = ['center', 'left', 'center', 'center', 'right'];
const textPosition = ['top', 'middle', 'bottom'];

function parseTextAlignment(pos: number) {
  return textAlignment[pos] ?? textAlignment[0];
}

function parseTextPosition(pos: number) {
  return textPosition[pos] ?? textPosition[0];
}

export async function parseViewNode(node: any): Promise<ModelViewNode> {
  const id = node['@identifier'];

  const name = decodeXML(node['ar3_label']?.[0]['value']),
    x = Number.parseFloat(node['@x'] ?? 0),
    y = Number.parseFloat(node['@y'] ?? 0),
    width = Number.parseFloat(node['@w'] ?? 0),
    height = Number.parseFloat(node['@h'] ?? 0);

  const styleOptions = {};
  styleOptions['textAlignment'] = parseTextAlignment(
    Number.parseInt(node['@textAlignment'], 10)
  );
  styleOptions['textPosition'] = parseTextPosition(
    Number.parseInt(node['@textPosition'], 10)
  );
  styleOptions['borderType'] = node['@borderType'] ?? 0;

  const style = 'ar3_style' in node ? node['ar3_style'] : {};

  const fillColor = style['ar3_fillColor'];

  if (fillColor) {
    styleOptions['fillColor'] = rgbToHex(
      Number.parseInt(fillColor['@r'], 10),
      Number.parseInt(fillColor['@g'], 10),
      Number.parseInt(fillColor['@b'], 10)
    );
  }

  const font = style['ar3_font'];
  if (font) {
    styleOptions['fontName'] = font['@name'];
    styleOptions['fontSize'] = font['@size'];

    const fontColor = font['ar3_color'];
    if (fontColor) {
      styleOptions['fontColor'] = rgbToHex(
        Number.parseInt(fontColor['@r'], 10),
        Number.parseInt(fontColor['@g'], 10),
        Number.parseInt(fontColor['@b'], 10)
      );
    }
  }

  let type = node['@xsi_type'],
    ref = node['@elementRef'];

  if (node['ar3_viewRef']) {
    type = 'ar3_ArchiDiagramModelReference';
    ref = node['ar3_viewRef']['@ref'];
  }

  const humanReadableType = humanReadableTypes[type];

  return {
    id,
    ref,
    name,
    type,
    humanReadableType,
    x,
    y,
    width,
    height,
    style: styleOptions,
    parserType: 'node',
  };
}
