<script setup lang="ts">
import { computed, ref, watchEffect } from "vue";
import type { Ref } from "vue";

import TreeSelect from "primevue/treeselect";
import type { TreeNode } from "primevue/treenode";

import { fetchConceptsTree } from "@/arches_component_lab/datatypes/concept/api.ts";
import type { ConceptListValue } from "@/arches_component_lab/datatypes/concept-list/types.ts";
import type { CardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import { convertSelectionToModelValue } from "@/arches_component_lab/datatypes/concept-list/utils.ts";

import type {
    CollectionItem,
    ConceptFetchResult,
} from "@/arches_component_lab/datatypes/concept/types.ts";

const { graphSlug, nodeAlias, aliasedNodeData, cardXNodeXWidgetData } =
    defineProps<{
        graphSlug: string;
        nodeAlias: string;
        aliasedNodeData: ConceptListValue;
        cardXNodeXWidgetData: CardXNodeXWidgetData;
    }>();

const emit = defineEmits<{
    (event: "update:value", updatedValue: ConceptListValue): void;
}>();

const options: Ref<CollectionItem[] | null> = ref<CollectionItem[] | null>(
    null,
);
const isLoading = ref(false);
const optionsLoaded = ref(false);
const optionsTotalCount = ref(0);
const fetchError = ref<string | null>(null);

const initialValue = computed<Record<string, boolean>>(() => {
    return (
        aliasedNodeData.node_value?.reduce(
            (acc: Record<string, boolean>, value: string) => {
                return { ...acc, [value]: true };
            },
            {},
        ) || {}
    );
});

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

function onUpdateModelValue(selectedConcepts: string[]) {
    const formattedValue: ConceptListValue = convertSelectionToModelValue(
        selectedConcepts,
        options.value ?? ([] as CollectionItem[]),
    );
    emit("update:value", formattedValue);
}
</script>

<template>
    <TreeSelect
        :id="nodeAlias"
        selection-mode="multiple"
        :fluid="true"
        filter
        :loading="isLoading"
        :model-value="initialValue"
        :options="options as TreeNode[]"
        :placeholder="cardXNodeXWidgetData.config.placeholder"
        @update:model-value="onUpdateModelValue"
    >
    </TreeSelect>
</template>
