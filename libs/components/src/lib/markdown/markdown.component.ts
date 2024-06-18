import { Component, Input } from '@angular/core';
import { MarkdownService } from 'ngx-markdown';

@Component({
  selector: 'models4insight-markdown',
  templateUrl: 'markdown.component.html',
  styleUrls: ['markdown.component.scss'],
})
export class MarkdownComponent {
  /**
   * The markdown content
   */
  @Input() markdown: string;

  constructor(private readonly markdownService: MarkdownService) {
    this.markdownService.renderer.blockquote = (quote) => {
      return `
        <article class="message">
          <div class="message-body">
            ${quote}
          </div>
        </article>
    `;
    };

    this.markdownService.renderer.image = (href, title, text) => {
      return `
        <figure class="image" title="${title}">
          <img src="${href}" alt="${text}">
        </figure>
      `;
    };

    this.markdownService.renderer.heading = (text, level) => {
      return `
        <h${level} class="title is-${level}">
          ${text}
        </h${level}>
      `;
    };

    this.markdownService.renderer.table = (header, body) => {
      return `
        <div class="table-container">
          <table class="table is-striped is-hoverable is-fullwidth">
            ${header}
            ${body}
          </table>
        </div>
      `;
    };
  }
}
