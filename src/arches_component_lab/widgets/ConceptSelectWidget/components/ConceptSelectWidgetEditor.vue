<script setup lang="ts">
import { computed, ref, watchEffect } from "vue";
import type { Ref } from "vue";

import TreeSelect from "primevue/treeselect";
import type { TreeNode } from "primevue/treenode";

import { fetchConceptsTree } from "@/arches_component_lab/datatypes/concept/api.ts";
import { convertConceptOptionToFormValue } from "@/arches_component_lab/datatypes/concept/utils.ts";

import type {
    CollectionItem,
    ConceptValue,
    ConceptFetchResult,
} from "@/arches_component_lab/datatypes/concept/types.ts";
import type { CardXNodeXWidgetData } from "@/arches_component_lab/types.ts";

const { graphSlug, nodeAlias, aliasedNodeData, cardXNodeXWidgetData } =
    defineProps<{
        graphSlug: string;
        nodeAlias: string;
        aliasedNodeData: ConceptValue;
        cardXNodeXWidgetData: CardXNodeXWidgetData;
    }>();

const emit = defineEmits<{
    (event: "update:value", updatedValue: ConceptValue): void;
}>();

const options: Ref<CollectionItem[] | null> = ref<CollectionItem[] | null>(
    null,
);
const isLoading = ref(false);
const optionsLoaded = ref(false);
const optionsTotalCount = ref(0);
const fetchError = ref<string | null>(null);

const initialValue = computed<Record<string, boolean>>(
    (): Record<string, boolean> => {
        if (!aliasedNodeData?.node_value) return {};
        return { [aliasedNodeData.node_value]: true };
    },
);

watchEffect(() => {
    getOptions();
});

async function getOptions() {
    try {
        if (optionsLoaded.value) return;
        isLoading.value = true;

        const fetchedData: ConceptFetchResult = await fetchConceptsTree(
            graphSlug,
            nodeAlias,
        );

        options.value = fetchedData.results as CollectionItem[];

        optionsTotalCount.value = options.value.length;
    } catch (error) {
        fetchError.value = (error as Error).message;
    } finally {
        isLoading.value = false;
        optionsLoaded.value = true;
    }
}

function onUpdateModelValue(selectedOption: Record<string, boolean> | null) {
    const formattedValue = convertConceptOptionToFormValue(
        selectedOption,
        options.value ?? ([] as CollectionItem[]),
    );
    emit("update:value", formattedValue);
}
</script>

<template>
    <TreeSelect
        :id="nodeAlias"
        data-key="key"
        selection-mode="single"
        filter
        :fluid="true"
        :loading="isLoading"
        :model-value="initialValue"
        :options="options as TreeNode[]"
        :placeholder="cardXNodeXWidgetData.config.placeholder"
        :reset-filter-on-hide="true"
        @update:model-value="onUpdateModelValue"
    >
    </TreeSelect>
</template>
