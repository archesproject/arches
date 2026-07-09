<script setup lang="ts">
import { computed, ref, watch, watchEffect } from "vue";

import TreeSelect from "primevue/treeselect";

import { useConceptTreeStore } from "@/arches_component_lab/stores/useConceptTreeStore.ts";
import { buildConceptAliasedNodeData } from "@/arches_component_lab/datatypes/concept/utils.ts";

import type { Ref } from "vue";
import type { TreeNode } from "primevue/treenode";
import type {
    CollectionItem,
    ConceptAliasedNodeData,
    ConceptFetchResult,
} from "@/arches_component_lab/datatypes/concept/types.ts";
import type { CardXNodeXWidgetData } from "@/arches_component_lab/types.ts";

const { graphSlug, nodeAlias, aliasedNodeData, cardXNodeXWidgetData } =
    defineProps<{
        graphSlug?: string;
        nodeAlias?: string;
        aliasedNodeData?: ConceptAliasedNodeData | null;
        cardXNodeXWidgetData?: CardXNodeXWidgetData;
    }>();

const emit = defineEmits<{
    (event: "update:isLoading", isLoading: boolean): void;
    (
        event: "update:aliasedNodeData",
        updatedValue: ConceptAliasedNodeData,
    ): void;
    (event: "initialized", updatedValue: ConceptAliasedNodeData): void;
}>();

const options: Ref<CollectionItem[] | null> = ref<CollectionItem[] | null>(
    null,
);
const isLoading = ref(false);
const optionsLoaded = ref(false);
const optionsTotalCount = ref(0);
const fetchError = ref<string | null>(null);

const initialValue = computed<Record<string, boolean> | null>(
    (): Record<string, boolean> | null => {
        if (!aliasedNodeData?.node_value) {
            return null;
        }
        return { [aliasedNodeData.node_value]: true };
    },
);

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
                    buildConceptAliasedNodeData(null, options.value ?? []),
            );
        }
        optionsLoaded.value = true;
    }
}

function onUpdateModelValue(selectedOption: Record<string, boolean> | null) {
    const id = selectedOption ? Object.keys(selectedOption)[0] ?? null : null;
    emit(
        "update:aliasedNodeData",
        buildConceptAliasedNodeData(id, options.value ?? []),
    );
}
</script>

<template>
    <TreeSelect
        :input-id="cardXNodeXWidgetData?.node.alias"
        data-key="key"
        selection-mode="single"
        filter
        :fluid="true"
        :show-clear="true"
        :loading="isLoading"
        :model-value="initialValue"
        :options="options as TreeNode[]"
        :placeholder="cardXNodeXWidgetData?.config.placeholder"
        :reset-filter-on-hide="true"
        @update:model-value="onUpdateModelValue"
    >
    </TreeSelect>
</template>
