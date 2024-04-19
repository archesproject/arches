<script setup lang="ts">
import arches from "arches";
import { computed, inject, ref } from "vue";
import { useGettext } from "vue3-gettext";

import Column from "primevue/column";
import DataTable from "primevue/datatable";
import Dropdown from "primevue/dropdown";
import InputText from "primevue/inputtext";
import { useToast } from "primevue/usetoast";

import { deleteLabel, upsertLabel } from "@/components/ControlledListManager/api.ts";
import AddLabel from "@/components/ControlledListManager/AddLabel.vue";

import { itemKey, ALT_LABEL, PREF_LABEL, URI } from "@/components/ControlledListManager/const.ts";

import type { DataTableRowEditInitEvent } from "primevue/datatable";
import type {
    ControlledListItem,
    Label,
    NewLabel,
    ValueType,
} from "@/types/ControlledListManager";
import type { Ref } from "@/types/Ref";

const props: { type: ValueType | "URI" } = defineProps(["type"]);
const { item, appendItemLabel, updateItemLabel, removeItemLabel } : {
    item: Ref<ControlledListItem>,
    appendItemLabel: Ref<(appendedLabel: Label | NewLabel) => undefined>,
    updateItemLabel: Ref<(updatedLabel: Label) => undefined>,
    removeItemLabel: Ref<(removedLabel: Label | NewLabel) => undefined>,
} = inject(itemKey);
const editingRows = ref([]);

const toast = useToast();
const { $gettext } = useGettext();
const slateBlue = "#2d3c4b"; // todo: import from theme somewhere

const headings: { heading: string; subheading: string } = computed(() => {
    switch (props.type) {
        case PREF_LABEL:
            return {
                heading: $gettext("Preferred Label(s)"),
                subheading: $gettext(
                    "Provide at least one preferred label and language for your list item."
                ),
            };
        case ALT_LABEL:
            return {
                heading: $gettext("Alternate Label(s)"),
                subheading: $gettext(
                    "Optionally, you can provide additional label/language labels for your list item. Useful if you want to make searching for labels with synonyms or common misspellings of your preferred label(s) easier."
                ),
            };
        case URI:
            return {
                heading: $gettext("List Item URI"),
                subheading: $gettext(
                    "Optionally, provide a URI for your list item. Useful if your list item is formally defined in a thesaurus or authority document."
                ),
            };
        default:
            return {
                heading: "",
                subheading: "",
            };
    }
});

const labels = computed(() => {
    if (!item.value) {
        return [];
    }
    return item.value.labels.filter(
        label => label.valuetype === props.type
    );
});

const onSave = async (event: DataTableRowEditInitEvent) => {
    // normalize new label numbers (starting at 1000) to null
    const normalizedNewData: Label = {
        ...event.newData,
        id: typeof event.newData.id === 'string' ? event.newData.id : null,
    };
    const upsertedLabel: Label = await upsertLabel(
        normalizedNewData,
        toast,
        $gettext,
    );
    if (normalizedNewData.id) {
        updateItemLabel.value(upsertedLabel);
    } else {
        appendItemLabel.value(upsertedLabel);
        removeItemLabel.value(event.newData);
    }
};

const onDelete = async (label: NewLabel | Label) => {
    if (typeof label.id === 'number') {
        removeItemLabel.value(label);
        return;
    }
    const deleted = await deleteLabel(label, toast, $gettext);
    if (deleted) {
        removeItemLabel.value(label);
    }
};
</script>

<template>
    <div class="label-editor-container">
        <h4>{{ headings.heading }}</h4>
        <h5>{{ headings.subheading }}</h5>
        <DataTable
            v-if="type !== URI"
            v-model:editingRows="editingRows"
            :value="labels"
            data-key="id"
            edit-mode="row"
            striped-rows
            scrollable
            :style="{ fontSize: 'small' }"
            @row-edit-save="onSave"
        >
            <Column field="value">
                <template #editor="{ data, field }">
                    <InputText
                        v-model="data[field]"
                        style="width: 90%"
                    />
                </template>
            </Column>
            <Column
                field="language"
                :header="$gettext('Language')"
                style="width: 10%; min-width: 12rem; height: 4rem;"
            >
                <template #editor="{ data, field }">
                    <Dropdown
                        v-model="data[field]"
                        :options="arches.languages"
                        option-label="name"
                        option-value="code"
                        :pt="{
                            input: { style: { fontFamily: 'inherit', fontSize: 'small' } },
                            panel: { style: { fontSize: 'small' } },
                        }"
                    />
                </template>
            </Column>
            <Column
                :row-editor="true"
                style="width: 10%; min-width: 8rem;"
            />
            <Column style="width: 5%;">
                <template #body="slotProps">
                    <i
                        class="fa fa-trash"
                        role="button"
                        tabindex="0"
                        :aria-label="$gettext('Delete')"
                        @click="onDelete(slotProps.data)"
                        @key.enter="onDelete(slotProps.data)"
                    />
                </template>
            </Column>
        </DataTable>
        <AddLabel
            v-if="type !== URI"
            :type="type"
        />
    </div>
</template>

<style scoped>
.label-editor-container {
    margin: 1rem 1rem 3rem 1rem;
    width: 80%;
}

h4 {
    color: v-bind(slateBlue);
    margin-top: 0;
    font-size: small;
}

h5 {
    font-weight: normal;
    margin-top: 0;
}

:deep(.p-editable-column) {
    padding-left: 0.5rem;
}
</style>
