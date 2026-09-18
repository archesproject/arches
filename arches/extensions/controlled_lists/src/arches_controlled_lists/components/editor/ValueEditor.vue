<script setup lang="ts">
import arches from "arches";
import { computed, inject, ref, useTemplateRef } from "vue";
import { useGettext } from "vue3-gettext";

import Column from "primevue/column";
import DataTable from "primevue/datatable";
import InputText from "primevue/inputtext";
import Select from "primevue/select";
import Textarea from "primevue/textarea";
import { useToast } from "primevue/usetoast";

import { deleteValue, upsertValue } from "@/arches_controlled_lists/api.ts";
import {
    ALT_LABEL,
    DEFAULT_ERROR_TOAST_LIFE,
    ERROR,
    NOTE,
    NOTE_CHOICES,
    PREF_LABEL,
    isEditingKey,
    itemKey,
} from "@/arches_controlled_lists/constants.ts";
import {
    commandeerFocusFromDataTable,
    dataIsNew,
    languageNameFromCode,
} from "@/arches_controlled_lists/utils.ts";
import AddValue from "@/arches_controlled_lists/components/editor/AddValue.vue";

import type { Ref } from "vue";
import type { DataTableRowEditInitEvent } from "primevue/datatable";
import type {
    ControlledListItem,
    IsEditingRefAndSetter,
    Language,
    Value,
    ValueCategory,
    ValueType,
} from "@/arches_controlled_lists/types";

const { valueType, valueCategory } = defineProps<{
    valueType?: ValueType;
    valueCategory?: ValueCategory;
}>();
const editingRows: Ref<Value[]> = ref([]);
const rowIndexToFocus = ref(-1);
const editorDiv = useTemplateRef("editorDiv");

const item = inject(itemKey) as Ref<ControlledListItem>;
const { isEditing, setIsEditing } = inject(
    isEditingKey,
) as IsEditingRefAndSetter;

const toast = useToast();
const { $gettext } = useGettext();
const valueHeader = $gettext("Value");
const languageHeader = $gettext("Language");
const noteTypeHeader = $gettext("Note type");

const labeledNoteChoices = [
    {
        type: NOTE_CHOICES.scope,
        label: $gettext("Scope note"),
    },
    {
        type: NOTE_CHOICES.definition,
        label: $gettext("Definition"),
    },
    {
        type: NOTE_CHOICES.example,
        label: $gettext("Example"),
    },
    {
        type: NOTE_CHOICES.history,
        label: $gettext("History note"),
    },
    {
        type: NOTE_CHOICES.editorial,
        label: $gettext("Editorial note"),
    },
    {
        type: NOTE_CHOICES.change,
        label: $gettext("Change note"),
    },
    {
        type: NOTE_CHOICES.note,
        label: $gettext("Note"),
    },
    {
        type: NOTE_CHOICES.description,
        label: $gettext("Description"),
    },
];

const noteChoiceLabel = (valueType: string) => {
    return labeledNoteChoices.find((choice) => choice.type === valueType)!
        .label;
};

const headings: Ref<{ heading: string; subheading: string }> = computed(() => {
    switch (valueType) {
        case PREF_LABEL:
            return {
                heading: $gettext("Preferred Label(s)"),
                subheading: $gettext(
                    "Provide at least one preferred label and language for your list item.",
                ),
            };
        case ALT_LABEL:
            return {
                heading: $gettext("Alternate Label(s)"),
                subheading: $gettext(
                    "Optionally, you can provide additional labels for your list item. Useful if you want to make searching for labels with synonyms or common misspellings of your preferred label(s) easier.",
                ),
            };
        default:
            return {
                heading: $gettext("Notes"),
                subheading: $gettext(
                    "Optionally, you can provide notes for your list item.",
                ),
            };
    }
});

const values = computed(() => {
    if (!item.value) {
        return [];
    }
    if (!valueType) {
        if (valueCategory === NOTE) {
            // Show everything but labels for now.
            // We're not returning category from the API, and images already excluded.
            return item.value.values.filter(
                (value) =>
                    ![PREF_LABEL, ALT_LABEL].includes(value.valuetype_id),
            );
        }
    }
    return item.value.values.filter(
        (value) => value.valuetype_id === valueType,
    );
});

const cursorClass = computed(() => {
    return isEditing.value ? "text" : "pointer";
});

const saveValue = async (event: DataTableRowEditInitEvent) => {
    setIsEditing(editingRows.value.length > 0);
    // normalize new value numbers to null
    const normalizedNewData: Value = {
        ...event.newData,
        id: dataIsNew(event.newData) ? null : event.newData.id,
        value: event.newData.value.trim(),
    };
    let upsertedValue: Value;
    try {
        upsertedValue = await upsertValue(normalizedNewData);
    } catch (error) {
        toast.add({
            severity: ERROR,
            life: DEFAULT_ERROR_TOAST_LIFE,
            summary: $gettext("Value save failed"),
            detail: error instanceof Error ? error.message : undefined,
        });
        if (normalizedNewData.id === null) {
            removeItemValue(event.newData);
        }
        return;
    }
    if (normalizedNewData.id) {
        updateItemValue(upsertedValue);
    } else {
        appendItemValue(upsertedValue);
        removeItemValue(event.newData);
    }
};

const issueDeleteValue = async (value: Value) => {
    makeRowUneditable(value.id);
    if (dataIsNew(value)) {
        removeItemValue(value);
        return;
    }
    try {
        await deleteValue(value);
    } catch (error) {
        toast.add({
            severity: ERROR,
            life: DEFAULT_ERROR_TOAST_LIFE,
            summary: $gettext("Value deletion failed"),
            detail: error instanceof Error ? error.message : undefined,
        });
        return;
    }
    removeItemValue(value);
};

const appendItemValue = (newValue: Value) => {
    item.value.values.push(newValue);
};

const removeItemValue = (removedValue: Value) => {
    const toDelete = item.value.values.findIndex(
        (valueFromItem) => valueFromItem.id === removedValue.id,
    );
    item.value.values.splice(toDelete, 1);
};

const updateItemValue = (updatedValue: Value) => {
    const toUpdate = item.value.values.find(
        (valueFromItem) => valueFromItem.id === updatedValue.id,
    );
    if (toUpdate) {
        toUpdate.language_id = updatedValue.language_id;
        toUpdate.value = updatedValue.value;
        toUpdate.valuetype_id = updatedValue.valuetype_id;
    }
};

const setRowFocus = (event: DataTableRowEditInitEvent) => {
    if (isEditing.value) {
        return;
    }
    setIsEditing(true);
    rowIndexToFocus.value = event.index;
};

function makeRowUneditable(valueId: string) {
    editingRows.value = [
        ...editingRows.value.filter((value) => value.id !== valueId),
    ];
    setIsEditing(editingRows.value.length > 0);
}

const makeValueEditable = (clickedValue: Value, index: number) => {
    if (isEditing.value) {
        return;
    }
    setIsEditing(true);
    if (!editingRows.value.includes(clickedValue)) {
        editingRows.value = [...editingRows.value, clickedValue];
    }
    if (index === -1) {
        // Coming from <AddValue>
        rowIndexToFocus.value = Math.max(values.value.length - 1, 0);
    } else {
        rowIndexToFocus.value = index;
    }
};

const inputSelector = computed(() => {
    return `[data-p-index="${rowIndexToFocus.value}"]`;
});

const focusInput = () => {
    if (rowIndexToFocus.value !== -1) {
        // Note editor uses the second column.
        const indexOfInputCol = valueCategory ? 1 : 0;
        const rowEl = editorDiv.value!.querySelector(inputSelector.value);
        const inputEl = rowEl!.children[indexOfInputCol]
            .children[0] as HTMLInputElement;
        commandeerFocusFromDataTable(inputEl);
        rowIndexToFocus.value = -1;
    }
};
</script>

<template>
    <div
        ref="editorDiv"
        class="value-editor-container"
    >
        <div class="value-editor-title">
            <h4>{{ headings.heading }}</h4>
            <AddValue
                :value-type
                :make-new-value-editable="makeValueEditable"
            />
        </div>
        <p>{{ headings.subheading }}</p>

        <div class="value-editor-table">
            <DataTable
                v-if="values.length"
                v-model:editing-rows="editingRows"
                :value="values"
                data-key="id"
                edit-mode="row"
                striped-rows
                scrollable
                :style="{ fontSize: 'small' }"
                @row-edit-cancel="(event) => makeRowUneditable(event.data.id)"
                @row-edit-init="setRowFocus"
                @row-edit-save="saveValue"
            >
                <!-- Note type select (if this is a note editor) -->
                <Column
                    v-if="valueCategory"
                    field="valuetype_id"
                    :header="noteTypeHeader"
                    style="width: 20%"
                >
                    <template #editor="{ data, field }">
                        <Select
                            v-model="data[field]"
                            :options="labeledNoteChoices"
                            option-label="label"
                            option-value="type"
                            :pt="{
                                root: { style: { width: '90%' } },
                                optionLabel: { style: { fontSize: 'small' } },
                            }"
                        />
                    </template>
                    <template #body="slotProps">
                        {{ noteChoiceLabel(slotProps.data.valuetype_id) }}
                    </template>
                </Column>
                <Column
                    field="value"
                    :header="valueHeader"
                    style="width: 60%; min-width: 8rem"
                >
                    <template #editor="{ data, field }">
                        <!-- Textarea for notes, input for labels -->
                        <Textarea
                            v-if="valueCategory"
                            v-model="data[field]"
                            rows="3"
                            cols="60"
                            auto-resize
                            :pt="{
                                hooks: {
                                    onMounted: focusInput,
                                    onUpdated: focusInput,
                                },
                            }"
                            :style="{ fontSize: 'small' }"
                        />
                        <InputText
                            v-else
                            v-model="data[field]"
                            :pt="{
                                hooks: {
                                    onMounted: focusInput,
                                    onUpdated: focusInput,
                                },
                            }"
                        />
                    </template>
                    <template #body="slotProps">
                        <span
                            class="full-width-pointer"
                            style="white-space: pre-wrap"
                            @click.stop="
                                makeValueEditable(
                                    slotProps.data,
                                    slotProps.index,
                                )
                            "
                        >
                            {{ slotProps.data.value }}
                        </span>
                    </template>
                </Column>
                <Column
                    field="language_id"
                    :header="languageHeader"
                    style="width: 12%; height: 5rem"
                >
                    <template #editor="{ data, field }">
                        <Select
                            v-model="data[field]"
                            :options="arches.languages"
                            :option-label="
                                (lang: Language) =>
                                    `${lang.name} (${lang.code})`
                            "
                            option-value="code"
                            :pt="{
                                optionLabel: { style: { fontSize: 'small' } },
                            }"
                        />
                    </template>
                    <template #body="slotProps">
                        {{
                            `${languageNameFromCode(slotProps.data.language_id)} (${slotProps.data.language_id})`
                        }}
                    </template>
                </Column>
                <Column
                    :row-editor="true"
                    style="width: 5%; text-align: center; white-space: nowrap"
                    :pt="{
                        headerCell: {
                            ariaLabel: $gettext('Row edit controls'),
                        },
                        pcRowEditorInit: {},
                    }"
                >
                    <template #roweditoriniticon>
                        <i
                            class="fa fa-pencil"
                            aria-hidden="true"
                        ></i>
                    </template>
                    <template #roweditorsaveicon>
                        <i
                            class="fa fa-check"
                            aria-hidden="true"
                        ></i>
                    </template>
                    <template #roweditorcancelicon>
                        <i
                            class="fa fa-undo"
                            aria-hidden="true"
                        ></i>
                    </template>
                </Column>
                <Column
                    style="width: 5%; text-align: center; white-space: nowrap"
                    :pt="{
                        headerCell: { ariaLabel: $gettext('Delete controls') },
                    }"
                >
                    <template #body="slotProps">
                        <i
                            class="fa fa-trash"
                            role="button"
                            tabindex="0"
                            :aria-label="$gettext('Delete')"
                            @click="issueDeleteValue(slotProps.data)"
                            @keyup.enter="issueDeleteValue(slotProps.data)"
                        ></i>
                    </template>
                </Column>
            </DataTable>
        </div>
    </div>
</template>

<style scoped>
.value-editor-container {
    margin: 1rem 1rem 4rem 2rem;
}

.value-editor-title {
    display: flex;
    gap: 1rem;
}

.value-editor-title h4 {
    font-size: 1.66rem;
    margin: 0;
    padding: 0.5rem 0 0 0;
    font-weight: 400;
}

.value-editor-container p {
    margin: 0;
    padding: 0.25rem 0 0 0;
    color: var(--p-text-muted-color);
}

i {
    font-size: var(--p-icon-size);
}

p {
    font-weight: normal;
    margin-top: 0;
}

.full-width-pointer {
    cursor: v-bind(cursorClass);
    display: flex;
    width: 100%;
}

:deep(td > input) {
    height: 3rem;
    font-size: inherit;
    border-radius: 2px;
}

:deep(td > input, textarea) {
    width: 100%;
}

:deep(.p-textarea) {
    border-radius: 2px;
}

:deep(.p-select) {
    border-radius: 2px;
}

:deep(.p-datatable-column-title) {
    font-size: small;
}

:deep(.p-button-text.p-button-secondary.p-datatable-row-editor-init) {
    background: var(--p-button-secondary-background);
}

:deep(.p-button-text.p-button-secondary.p-datatable-row-editor-init:hover) {
    background: var(--p-button-primary-hover-background);
    color: var(--p-button-primary-hover-color);
}

:deep(.p-button-text.p-button-secondary.p-datatable-row-editor-save:hover) {
    background: var(--p-button-primary-hover-background);
    color: var(--p-button-primary-hover-color);
}

:deep(
        .p-button.p-component.p-button-icon-only.p-button-secondary.p-button-rounded.p-button-text.p-datatable-row-editor-cancel:hover
    ) {
    background: var(--p-amber-300);
    color: var(--p-button-primary-hover-color);
}

:deep(i[role="button"]) {
    height: var(--p-button-icon-only-width);
    width: var(--p-button-icon-only-width);
    border-radius: 50%;
    border: 1px solid var(--p-button-secondary-border-color);
    background: var(--p-button-secondary-background);
    padding: 0.67rem;
}

:deep(i[role="button"]:hover) {
    background: var(--p-button-danger-background);
    color: var(--p-button-primary-hover-color);
}
</style>
