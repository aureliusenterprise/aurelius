import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { faEdit, faPlus, faTrash } from '@fortawesome/free-solid-svg-icons';
import { TypeDefsService } from '../services/type-defs/type-defs.service';
import {
    ClassificationInput,
    ClassificationRequestError,
    ClassificationsAdminService,
    ClassificationSummary,
} from './classifications-admin.service';

/** The entity types a classification can be attached to in the Aurelius editors */
export const CLASSIFIABLE_TYPES = [
    'm4i_data_entity',
    'm4i_data_attribute',
    'm4i_field',
    'm4i_dataset',
    'm4i_collection',
];

/** Technical name of a classification: a letter, then letters, digits or _ (as the backend checks it) */
const NAME_PATTERN = /^[A-Za-z][A-Za-z0-9_]{0,63}$/;

type FormMode = 'create' | 'edit';

/**
 * Classification management (administrators): the tenant's classifications with their use, and a form to create
 * and change them. Deleting is only possible for classifications that no entity carries.
 */
@Component({
    selector: 'models4insight-classifications-admin',
    templateUrl: 'classifications-admin.component.html',
    styleUrls: ['classifications-admin.component.scss'],
    providers: [ClassificationsAdminService],
})
export class ClassificationsAdminComponent implements OnInit {
    readonly faEdit = faEdit;
    readonly faPlus = faPlus;
    readonly faTrash = faTrash;

    classifications: ClassificationSummary[] = [];
    isLoading = false;
    loadError: string = null;

    /** Open form: create a new classification or edit an existing one */
    formMode: FormMode = null;
    isSaving = false;
    formError: string = null;
    /** The entity types offered as checkboxes: the Aurelius types and any others the classification already has */
    typeOptions: string[] = CLASSIFIABLE_TYPES;

    readonly form = new FormGroup({
        name: new FormControl('', [Validators.required, Validators.pattern(NAME_PATTERN)]),
        displayName: new FormControl('', [Validators.required]),
        displayNameNl: new FormControl(''),
        description: new FormControl(''),
        entityTypes: new FormControl<string[]>([], [Validators.required]),
    });
    /** Server message per form field (e.g. "name already used") */
    fieldErrors: { [field: string]: string } = {};

    /** The classification to delete, waiting for confirmation */
    deleteCandidate: ClassificationSummary = null;
    deleteError: string = null;
    isDeleting = false;

    constructor(
        private readonly api: ClassificationsAdminService,
        private readonly typeDefsService: TypeDefsService,
    ) {}

    ngOnInit() {
        this.load();
    }

    async load() {
        this.isLoading = true;
        this.loadError = null;
        try {
            this.classifications = await this.api.list();
        } catch (e) {
            this.loadError = e.message;
        } finally {
            this.isLoading = false;
        }
    }

    inUse(classification: ClassificationSummary): boolean {
        return classification.usage.direct + classification.usage.propagated > 0;
    }

    // ------------------------------------------------------------------ form
    openCreate() {
        this.form.reset({ name: '', displayName: '', displayNameNl: '', description: '', entityTypes: [] });
        this.form.controls.name.enable();
        this.typeOptions = CLASSIFIABLE_TYPES;
        this.openForm('create');
    }

    openEdit(classification: ClassificationSummary) {
        this.form.reset({
            name: classification.name,
            displayName: classification.displayName ?? classification.name,
            displayNameNl: classification.displayNames?.['nl-NL'] ?? '',
            description: classification.description ?? '',
            entityTypes: [...classification.entityTypes],
        });
        // the name identifies the classification everywhere: it cannot be changed
        this.form.controls.name.disable();
        this.typeOptions = [
            ...CLASSIFIABLE_TYPES,
            ...classification.entityTypes.filter((type) => !CLASSIFIABLE_TYPES.includes(type)),
        ];
        this.openForm('edit');
    }

    private openForm(mode: FormMode) {
        this.formMode = mode;
        this.formError = null;
        this.fieldErrors = {};
    }

    closeForm() {
        this.formMode = null;
    }

    isTypeSelected(type: string): boolean {
        return (this.form.controls.entityTypes.value ?? []).includes(type);
    }

    toggleType(type: string) {
        const selected = this.form.controls.entityTypes.value ?? [];
        this.form.controls.entityTypes.setValue(
            selected.includes(type) ? selected.filter((t) => t !== type) : [...selected, type],
        );
        this.form.controls.entityTypes.markAsTouched();
    }

    showError(field: 'name' | 'displayName' | 'displayNameNl' | 'description' | 'entityTypes'): boolean {
        const control = this.form.controls[field];
        return control.invalid && (control.touched || control.dirty);
    }

    async save() {
        this.form.markAllAsTouched();
        if (this.form.invalid) return;
        const value = this.form.getRawValue();
        const input: ClassificationInput = {
            name: value.name.trim(),
            displayName: value.displayName.trim(),
            displayNames: { 'nl-NL': (value.displayNameNl ?? '').trim() },
            description: (value.description ?? '').trim(),
            entityTypes: value.entityTypes,
        };
        this.isSaving = true;
        this.formError = null;
        this.fieldErrors = {};
        try {
            if (this.formMode === 'create') {
                await this.api.create(input);
            } else {
                await this.api.update(input.name, input);
            }
            this.formMode = null;
            // the editors and the classification labels use the type definitions: load them again
            await Promise.all([this.load(), this.typeDefsService.refresh()]);
        } catch (e) {
            if (e instanceof ClassificationRequestError && e.field) {
                this.fieldErrors = { [e.field === 'displayNames' ? 'displayNameNl' : e.field]: e.message };
            } else {
                this.formError = e.message;
            }
        } finally {
            this.isSaving = false;
        }
    }

    // ------------------------------------------------------------------ delete
    askDelete(classification: ClassificationSummary) {
        this.deleteCandidate = classification;
        this.deleteError = null;
    }

    cancelDelete() {
        this.deleteCandidate = null;
    }

    async confirmDelete() {
        if (!this.deleteCandidate) return;
        this.isDeleting = true;
        this.deleteError = null;
        try {
            await this.api.delete(this.deleteCandidate.name);
            this.deleteCandidate = null;
            await Promise.all([this.load(), this.typeDefsService.refresh()]);
        } catch (e) {
            this.deleteError = e.message;
        } finally {
            this.isDeleting = false;
        }
    }
}
