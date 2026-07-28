<script setup lang="ts">
import { computed, ref, watch, watchEffect } from "vue";

import Checkbox from "primevue/checkbox";
import CheckboxGroup from "primevue/checkboxgroup";

import { useConceptTreeStore } from "@/arches_vue_components/stores/useConceptTreeStore.ts";
import { buildConceptListAliasedNodeData } from "@/arches_vue_components/datatypes/concept-list/utils.ts";
import { flattenCollectionItems } from "@/arches_vue_components/datatypes/concept/utils.ts";
import { getOption } from "@/arches_vue_components/datatypes/concept/utils.ts";

import type { ConceptCardXNodeXWidgetData } from "@/arches_vue_components/types.ts";
import type {
    CollectionItem,
    ConceptValueItem,
    ConceptFetchResult,
} from "@/arches_vue_components/datatypes/concept/types.ts";
import type { ConceptListAliasedNodeData } from "@/arches_vue_components/datatypes/concept-list/types.ts";

const { graphSlug, nodeAlias, aliasedNodeData, cardXNodeXWidgetData } =
    defineProps<{
        graphSlug?: string;
        nodeAlias?: string;
        aliasedNodeData?: ConceptListAliasedNodeData | null;
        cardXNodeXWidgetData?: ConceptCardXNodeXWidgetData;
    }>();

const emit = defineEmits<{
    (event: "update:isLoading", isLoading: boolean): void;
    (
        event: "update:aliasedNodeData",
        updatedValue: ConceptListAliasedNodeData,
    ): void;
    (event: "initialized", updatedValue: ConceptListAliasedNodeData): void;
}>();

const flexDirection =
    cardXNodeXWidgetData?.config?.groupDirection === "column"
        ? "flex-column"
        : "flex-row";

const options = ref<CollectionItem[]>([]);
const isLoading = ref(false);
const optionsLoaded = ref(false);
const optionsTotalCount = ref(0);
const fetchError = ref<string | null>(null);

const initialValue = computed<string[] | null>(() => {
    if (!aliasedNodeData?.node_value?.length) return null;
    if (!options.value) return null;
    const result = [];
    for (const id of aliasedNodeData.node_value) {
        const option = getOption(id, options.value);
        if (option) {
            result.push(option.key);
        } else {
            // the option was not found using the key(valueid),
            // try to find it in the details array using valueid
            // and then mathching on the concept_id of the detail
            if (aliasedNodeData?.details?.length) {
                const detail = aliasedNodeData.details.find(
                    (detailItem: ConceptValueItem) => detailItem.valueid === id,
                );
                if (detail) {
                    const option = getOption(detail.concept_id, options.value);
                    if (option) {
                        result.push(option.key);
                    }
                }
            }
        }
    }
    return result.length ? result : null;
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

        options.value = flattenCollectionItems(fetchedData.results);
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

function onUpdateModelValue(updatedValue: string[] | null) {
    const nodeValues = updatedValue?.length ? updatedValue : null;
    emit(
        "update:aliasedNodeData",
        buildConceptListAliasedNodeData(nodeValues, options.value),
    );
}
</script>

<template>
    <CheckboxGroup
        :id="cardXNodeXWidgetData?.node.alias"
        :model-value="initialValue"
        :class="['button-group', flexDirection]"
        tabindex="-1"
        @update:model-value="onUpdateModelValue($event)"
    >
        <div
            v-for="option in options"
            :key="option.key"
            class="checkbox-options"
        >
            <Checkbox
                :input-id="option.key"
                :value="option.key"
            />
            <label :for="option.key">{{ option.label }}</label>
        </div>
    </CheckboxGroup>
</template>

<style scoped>
.p-checkbox {
    margin-right: 0.5rem;
}

label {
    all: unset;
}
.button-group {
    display: flex;
    flex-direction: row;
    column-gap: 1.5rem;
    row-gap: 0.5rem;
    flex-wrap: wrap;
}

.checkbox-options {
    display: flex;
    gap: 0.25rem;
    align-items: center;
}
.flex-column {
    flex-direction: column;
}
.flex-row {
    flex-direction: row;
    align-items: center;
}
</style>
