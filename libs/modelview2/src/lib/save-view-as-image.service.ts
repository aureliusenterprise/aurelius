import { Injectable } from '@angular/core';
import { AuthenticationService } from '@models4insight/authentication';
import { BasicStore, MonitorAsync } from '@models4insight/redux';
import { ModelService } from '@models4insight/services/model';
import { ProjectService } from '@models4insight/services/project';
import { ManagedTask } from '@models4insight/task-manager';
import {
  b64toBlob,
  bytesToBinaryString,
  saveAsFile,
  untilDestroyed,
} from '@models4insight/utils';
import { VersionService } from '@models4insight/version';
import html2canvas from 'html2canvas';
import { now } from 'lodash';
import { Subject } from 'rxjs';
import { exhaustMap, first } from 'rxjs/operators';
import { ModelExplorerService } from './model-explorer.service';
import { ModelviewService } from './model-view.service';
import { createChunk, joinChunk, splitChunk } from './utils/png-metadata';

interface PNGMetadata {
  /** Short (one line) title or caption for image */
  readonly Title?: string;
  /** Name of image's creator */
  readonly Author?: string;
  /** Description of image (possibly long) */
  readonly Description?: string;
  /** Copyright notice */
  readonly Copyright?: string;
  /** Time of original image creation */
  readonly 'Creation Time'?: number | string;
  /** Software used to create the image */
  readonly Software?: string;
  /** Legal disclaimer */
  readonly Disclaimer?: string;
  /** Warning of nature of content */
  readonly Warning?: string;
  /** Device used to create the image */
  readonly Source?: string;
  /** Miscellaneous comment; conversion from GIF comment */
  readonly Comment?: string;
}

async function addMetadata(
  png: string,
  metadata: PNGMetadata
): Promise<string> {
  // Split the PNG string into chunks
  const chunks = splitChunk(png);

  if (!chunks) throw Error('Input data does not have a PNG signature!');

  // Remove end marker
  const iend = chunks.pop();

  // Add metadata fields
  for (const [keyword, value] of Object.entries(metadata)) {
    if (!value) continue;
    const chunk = createChunk('tEXt', `${keyword}\0${value}`);
    chunks.push(chunk);
  }

  // Add back end marker
  chunks.push(iend);

  // Assemble the chunks into another PNG string
  return joinChunk(chunks);
}

async function canvasToBinaryString(canvas: HTMLCanvasElement) {
  const blob = await new Promise<Blob>((resolve) => canvas.toBlob(resolve));

  if (!blob) return '';

  return new Promise<string>((resolve) => {
    const reader = new FileReader();
    reader.onload = () => {
      const bytes = new Uint8Array(reader.result as ArrayBuffer),
        binary = bytesToBinaryString(bytes);

      resolve(binary);
    };
    reader.readAsArrayBuffer(blob);
  });
}

/**
 * Fallback function for browsers that taint the canvas when drawing an SVG with foreign objects
 */
async function drawHTML2Canvas(
  svg: SVGElement,
  width: number,
  height: number
): Promise<string> {
  const container = svg.parentElement;

  const canvas = await html2canvas(container, {
    logging: false,
    width: width,
    height: height,
    scrollY: -window.scrollY,
    scrollX: -window.scrollX,

    // Html2Canvas creates its own internal representation of the document. Do some cleanup before taking the image.
    onclone: (clonedDocument) => {
      const clonedContainer = clonedDocument.getElementById(
        'screenshot-container'
      );
      // This ensures the absolute width and height are actually applied
      clonedContainer.parentElement.style.display = 'inline';
      clonedContainer.style.width = `${width}px`;
      clonedContainer.style.height = `${height}px`;
    },
  });

  return canvasToBinaryString(canvas);
}

/**
 * Draws the given SVG to a canvas and returns it as a PNG blob
 */
async function drawSVG2Canvas(
  svg: SVGElement,
  width: number,
  height: number
): Promise<string> {
  // Firefox requires fixed dimensions to be set on the SVG before drawing it to a canvas.
  const copy = svg.cloneNode(true) as SVGElement;
  copy.setAttribute('width', width.toString());
  copy.setAttribute('height', height.toString());

  const data = new XMLSerializer().serializeToString(copy);
  const svgBlob = new Blob([data], { type: 'image/svg+xml' });
  const url = URL.createObjectURL(svgBlob);

  const img = new Image();

  const onImageLoaded = new Promise<Event>((resolve) => (img.onload = resolve));
  img.src = url;
  await onImageLoaded;

  URL.revokeObjectURL(url);

  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;

  const ctx = canvas.getContext('2d');
  ctx.drawImage(img, 0, 0);

  return canvasToBinaryString(canvas);
}

export interface SaveViewAsImageStoreContext {
  readonly isConverting?: boolean;
}

const defaultState: SaveViewAsImageStoreContext = {
  isConverting: false,
};

type SaveViewAsImageContext = [SVGElement, number, number];

@Injectable()
export class SaveViewAsImageService extends BasicStore<SaveViewAsImageStoreContext> {
  private readonly viewConverted$ = new Subject<Blob>();
  private readonly convert$ = new Subject<SaveViewAsImageContext>();

  constructor(
    private readonly authenticationService: AuthenticationService,
    private readonly modelService: ModelService,
    private readonly modelExplorerService: ModelExplorerService,
    private readonly modelviewService: ModelviewService,
    private readonly projectService: ProjectService,
    private readonly versionService: VersionService
  ) {
    super({ defaultState });
    this.init();
  }

  private init() {
    // Handle one conversion at a time. Ignore new requests while one is still in progress
    this.convert$
      .pipe(
        exhaustMap(([svg, width, height]) =>
          this.handleConvert(svg, width, height)
        ),
        untilDestroyed(this)
      )
      .subscribe(this.viewConverted$);
  }

  /**
   * Trigger the converison of the given svg to an image with the given width an height.
   * If you want an image of the complete svg, the width and height should account for any scaling.
   *
   * @param svg The svg definition
   * @param width The width of the image
   * @param height The height of the image
   */
  async convertViewToImage(svg: SVGElement, width: number, height: number) {
    this.convert$.next([svg, width, height]);
    return this.viewConverted.pipe(first()).toPromise();
  }

  /**
   * Trigger the converison of the given svg to an image with the given width an height.
   * Also saves the image as a file.
   * If you want an image of the complete svg, the width and height should account for any scaling.
   *
   * @param svg The svg definition
   * @param width The width of the image
   * @param height The height of the image
   */
  async saveViewAsImage(svg: SVGElement, width: number, height: number) {
    const viewId = await this.modelviewService.get('viewId'),
      view = await this.modelExplorerService.get(['views', viewId]);

    const png = await this.convertViewToImage(svg, width, height);

    if (png) saveAsFile(png, `${view.name}.png`);
  }

  get viewConverted() {
    return this.viewConverted$.asObservable();
  }

  @ManagedTask('Creating images for all views', { isQuiet: true })
  @ManagedTask('Creating an image of the view', { isQuiet: true })
  @MonitorAsync('isConverting')
  private async handleConvert(svg: SVGElement, width: number, height: number) {
    const viewId = await this.modelviewService.get('viewId'),
      view = await this.modelExplorerService.get(['views', viewId]);

    let png: string = null;

    // Some browsers (e.g. Chrome) cannot handle drawing SVGs with foreign objects to a canvas.
    // These browsers will throw an error when exporting the image.
    // Use a slower fallback method if an error is thrown at this step.
    try {
      png = await drawSVG2Canvas(svg, width, height);
    } catch {
      png = await drawHTML2Canvas(svg, width, height);
    }

    // If a png was successfully exported, add metadata tags and save the image as a file
    if (png) {
      const [author, branch, projectId, version] = await Promise.all([
        this.authenticationService.get(['credentials', 'email']),
        this.modelService.get('branch', { includeFalsy: true }),
        this.projectService.get('projectId', { includeFalsy: true }),
        this.modelService.get('version', { includeFalsy: true }),
      ]);

      let source = 'Generated model';
      if (projectId && branch) {
        source = `${projectId}/${branch}/${version}/${viewId}`;
      }

      const software = `Models4Insight/${this.versionService.appName}/${this.versionService.appVersion}`;

      const metadata: PNGMetadata = {
        Title: view.name,
        Author: author,
        Description: view.description,
        'Creation Time': now(),
        Software: software,
        Source: source,
      };

      const pngWithMetadata = await addMetadata(png, metadata);

      return b64toBlob(btoa(pngWithMetadata));
    }
  }
}
