<script setup lang="ts">
import { computed, ref, watch, watchEffect } from "vue";

import TreeSelect from "primevue/treeselect";

import { useConceptTreeStore } from "@/arches_component_lab/stores/useConceptTreeStore.ts";
import { buildConceptListAliasedNodeData } from "@/arches_component_lab/datatypes/concept-list/utils.ts";

import type { Ref } from "vue";
import type { TreeNode } from "primevue/treenode";
import type { CardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import type {
    CollectionItem,
    ConceptFetchResult,
} from "@/arches_component_lab/datatypes/concept/types.ts";
import type { ConceptListAliasedNodeData } from "@/arches_component_lab/datatypes/concept-list/types.ts";

const { graphSlug, nodeAlias, aliasedNodeData, cardXNodeXWidgetData } =
    defineProps<{
        graphSlug?: string;
        nodeAlias?: string;
        aliasedNodeData?: ConceptListAliasedNodeData | null;
        cardXNodeXWidgetData?: CardXNodeXWidgetData;
    }>();

const emit = defineEmits<{
    (event: "update:isLoading", isLoading: boolean): void;
    (
        event: "update:aliasedNodeData",
        updatedValue: ConceptListAliasedNodeData,
    ): void;
    (event: "initialized", updatedValue: ConceptListAliasedNodeData): void;
}>();

const options: Ref<CollectionItem[] | null> = ref<CollectionItem[] | null>(
    null,
);
const isLoading = ref(false);
const optionsLoaded = ref(false);
const optionsTotalCount = ref(0);
const fetchError = ref<string | null>(null);

const initialValue = computed<Record<string, boolean> | null>(() => {
    return (
        aliasedNodeData?.node_value?.reduce(
            (acc: Record<string, boolean>, id: string) => ({
                ...acc,
                [id]: true,
            }),
            {},
        ) ?? null
    );
});

watch(isLoading, (newValue) => {
    emit("update:isLoading", newValue);
});

watchEffect(() => {
    getOptions();
});

async function getOptions() {
    try {
        if (optionsLoaded.value) {
            return;
        }
        if (!graphSlug || !nodeAlias) {
            return;
        }
        isLoading.value = true;

        const fetchedData: ConceptFetchResult =
            await useConceptTreeStore().fetchTree(graphSlug, nodeAlias);

        options.value = fetchedData.results as CollectionItem[];
        optionsTotalCount.value = options.value.length;
    } catch (error) {
        fetchError.value = (error as Error).message;
    } finally {
        isLoading.value = false;
        if (!optionsLoaded.value) {
            emit(
                "initialized",
                aliasedNodeData ??
                    buildConceptListAliasedNodeData(null, options.value ?? []),
            );
        }
        optionsLoaded.value = true;
    }
}

function onUpdateModelValue(selection: Record<string, boolean> | null) {
    const nodeValues = selection ? Object.keys(selection) : null;
    emit(
        "update:aliasedNodeData",
        buildConceptListAliasedNodeData(nodeValues, options.value ?? []),
    );
}
</script>

<template>
    <TreeSelect
        :input-id="cardXNodeXWidgetData?.node.alias"
        selection-mode="multiple"
        :fluid="true"
        filter
        :show-clear="true"
        :loading="isLoading"
        :model-value="initialValue"
        :options="options as TreeNode[]"
        :placeholder="cardXNodeXWidgetData?.config.placeholder"
        @update:model-value="onUpdateModelValue"
    >
    </TreeSelect>
</template>
