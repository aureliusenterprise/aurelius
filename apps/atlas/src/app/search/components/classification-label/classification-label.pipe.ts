import { OnDestroy, Pipe, PipeTransform } from '@angular/core';
import { ClassificationDef } from '@models4insight/atlas/api';
import { TranslateService } from '@ngx-translate/core';
import { Subscription } from 'rxjs';
import { TypeDefsService } from '../../services/type-defs/type-defs.service';

/**
 * The name of a classification as users see it: the display name of the current language from the classification
 * definition (options "displayName.<language>", then "displayName"), else the translation of the technical name
 * (the classifications of older models), else the technical name. Takes a definition or a classification name.
 */
export function classificationLabel(
    def: ClassificationLike | undefined,
    name: string,
    language: string,
    translate: (key: string) => string,
): string {
    const options = (def?.options ?? {}) as Record<string, string>;
    return (
        options[`displayName.${language}`] ||
        options['displayName'] ||
        def?.displayNames?.[language] ||
        def?.displayName ||
        translate(name) ||
        name
    );
}

/** A classification definition, or a row of the classification management API (displayName, displayNames) */
export type ClassificationLike = Partial<ClassificationDef> & {
    readonly displayName?: string;
    readonly displayNames?: { readonly [language: string]: string };
};

@Pipe({ name: 'classificationLabel', pure: false })
export class ClassificationLabelPipe implements PipeTransform, OnDestroy {
    private defsByName: Record<string, ClassificationDef> = {};
    private readonly subscription: Subscription;

    constructor(
        private readonly translateService: TranslateService,
        typeDefsService: TypeDefsService,
    ) {
        this.subscription = typeDefsService
            .select(['typeDefs', 'classificationDefs'])
            .subscribe((defs: ClassificationDef[]) => {
                this.defsByName = Object.fromEntries((defs ?? []).map((def) => [def.name, def]));
            });
    }

    transform(value: string | ClassificationLike | null | undefined): string {
        if (!value) return '';
        const name = typeof value === 'string' ? value : value.name;
        // the loaded type definitions are the newest (they are reloaded after every change): they come first
        const def = typeof value === 'string' ? this.defsByName[value] : { ...value, ...this.defsByName[name] };
        const language = this.translateService.currentLang || this.translateService.defaultLang;
        return classificationLabel(def, name, language, (key) => this.translateService.instant(key));
    }

    ngOnDestroy() {
        this.subscription.unsubscribe();
    }
}
