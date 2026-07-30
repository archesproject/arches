<script setup lang="ts">
import { computed, ref, watch, watchEffect } from "vue";

import TreeSelect from "primevue/treeselect";

import { useConceptTreeStore } from "@/arches_vue_components/stores/useConceptTreeStore.ts";
import {
    buildConceptAliasedNodeData,
    getOption,
} from "@/arches_vue_components/datatypes/concept/utils.ts";

import type { Ref } from "vue";
import type { TreeNode } from "primevue/treenode";
import type {
    CollectionItem,
    ConceptAliasedNodeData,
    ConceptFetchResult,
    ConceptValueItem,
} from "@/arches_vue_components/datatypes/concept/types.ts";
import type { CardXNodeXWidgetData } from "@/arches_vue_components/types.ts";

const {
    graphSlug = undefined,
    nodeAlias = undefined,
    aliasedNodeData = null,
    cardXNodeXWidgetData = undefined,
} = defineProps<{
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
        if (options.value) {
            const option = getOption(aliasedNodeData.node_value, options.value);
            if (option) {
                return { [option.key]: true };
            } else {
                // the option was not found using the key(valueid),
                // try to find it in the details array using valueid
                // and then mathching on the concept_id of the detail
                if (aliasedNodeData?.details?.length) {
                    const detail = aliasedNodeData.details.find(
                        (detailItem: ConceptValueItem) =>
                            detailItem.valueid === aliasedNodeData.node_value,
                    );
                    if (detail) {
                        const option = getOption(
                            detail.concept_id,
                            options.value,
                        );
                        if (option) {
                            return { [option.key]: true };
                        }
                    }
                }
            }
        }
        return null;
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
