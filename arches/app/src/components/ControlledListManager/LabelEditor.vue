<script setup lang="ts">
import arches from "arches";
import { computed, ref } from "vue";
import { useGettext } from "vue3-gettext";

import Column from "primevue/column";
import DataTable from "primevue/datatable";
import Dropdown from "primevue/dropdown";
import InputText from "primevue/inputtext";
import { useToast } from "primevue/usetoast";

import { deleteLabel, upsertLabel } from "@/components/ControlledListManager/api.ts";
import AddLabel from "@/components/ControlledListManager/AddLabel.vue";

import { ALT_LABEL, PREF_LABEL } from "@/components/ControlledListManager/const.ts";
import { languageName } from "@/components/ControlledListManager/utils.ts";

import type { DataTableRowEditInitEvent } from "primevue/datatable";
import type {
    ControlledListItem,
    Label,
    NewLabel,
    ValueType,
} from "@/types/ControlledListManager";

const props: {
    type: ValueType,
    item: ControlledListItem,
    appendItemLabel: (appendedLabel: Label | NewLabel) => undefined,
    updateItemLabel: (updatedLabel: Label) => undefined,
    removeItemLabel: (removedLabel: Label | NewLabel) => undefined,
} = defineProps(["type", "item", "appendItemLabel", "updateItemLabel", "removeItemLabel"]);
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
        default:
            return {
                heading: "",
                subheading: "",
            };
    }
});

const labels = computed(() => {
    if (!props.item) {
        return [];
    }
    return props.item.labels.filter(
        label => label.valuetype_id === props.type
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
        props.updateItemLabel(upsertedLabel);
    } else {
        props.appendItemLabel(upsertedLabel);
        props.removeItemLabel(event.newData);
    }
};

const onDelete = async (label: NewLabel | Label) => {
    if (typeof label.id === 'number') {
        props.removeItemLabel(label);
        return;
    }
    const deleted = await deleteLabel(label, toast, $gettext);
    if (deleted) {
        props.removeItemLabel(label);
    }
};
</script>

<template>
    <div class="label-editor-container">
        <h4>{{ headings.heading }}</h4>
        <p>{{ headings.subheading }}</p>
        <DataTable
            v-if="labels.length"
            v-model:editingRows="editingRows"
            :value="labels"
            data-key="id"
            edit-mode="row"
            striped-rows
            scrollable
            :style="{ fontSize: 'small' }"
            @row-edit-save="onSave"
        >
            <Column
                field="value"
                style="min-width: 8rem"
            >
                <template #editor="{ data, field }">
                    <InputText v-model="data[field]" />
                </template>
            </Column>
            <Column
                field="language_id"
                :header="$gettext('Language')"
                style="width: 10%; min-width: 8rem; height: 4rem"
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
                <template #body="slotProps">
                    {{ languageName(slotProps.data.language_id) }}
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
        <AddLabel :type="type" />
    </div>
</template>

<style scoped>
.label-editor-container {
    margin: 1rem 1rem 3rem 1rem;
    width: 100%;
}

h4 {
    color: v-bind(slateBlue);
    margin-top: 0;
    font-size: small;
}

p {
    font-weight: normal;
    margin-top: 0;
    font-size: small;
}

:deep(th) {
    font-weight: 600;
}

:deep(td) {
    padding-left: 0.75rem;
}
</style>
