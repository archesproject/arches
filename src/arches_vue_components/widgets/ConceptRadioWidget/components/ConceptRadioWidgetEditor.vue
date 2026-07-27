<script setup lang="ts">
import { computed, ref, watch, watchEffect } from "vue";

import RadioButton from "primevue/radiobutton";
import RadioButtonGroup from "primevue/radiobuttongroup";

import { useConceptTreeStore } from "@/arches_vue_components/stores/useConceptTreeStore.ts";
import type {
    ConceptFetchResult,
    CollectionItem,
    ConceptValueItem,
    ConceptAliasedNodeData,
} from "@/arches_vue_components/datatypes/concept/types.ts";

import {
    buildConceptAliasedNodeData,
    flattenCollectionItems,
    getOption,
} from "@/arches_vue_components/datatypes/concept/utils.ts";
import type { ConceptCardXNodeXWidgetData } from "@/arches_vue_components/types.ts";

const { graphSlug, nodeAlias, aliasedNodeData, cardXNodeXWidgetData } =
    defineProps<{
        graphSlug?: string;
        nodeAlias?: string;
        aliasedNodeData?: ConceptAliasedNodeData | null;
        cardXNodeXWidgetData?: ConceptCardXNodeXWidgetData;
    }>();

const emit = defineEmits<{
    (event: "update:isLoading", isLoading: boolean): void;
    (
        event: "update:aliasedNodeData",
        updatedValue: ConceptAliasedNodeData,
    ): void;
    (event: "initialized", updatedValue: ConceptAliasedNodeData): void;
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

const initialValue = computed<string | null>(() => {
    if (!aliasedNodeData?.node_value) return null;
    if (options.value.length) {
        const option = getOption(aliasedNodeData.node_value, options.value);
        if (option) {
            return option.key;
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
                    const option = getOption(detail.concept_id, options.value);
                    if (option) {
                        return option.key;
                    }
                }
            }
        }
        return null;
    }
    return aliasedNodeData.node_value;
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
                    buildConceptAliasedNodeData(null, options.value ?? []),
            );
        }
        optionsLoaded.value = true;
    }
}

function onUpdateModelValue(updatedValue: string | null) {
    const nodeValue = updatedValue ?? null;
    emit(
        "update:aliasedNodeData",
        buildConceptAliasedNodeData(nodeValue, options.value),
    );
}
</script>

<template>
    <RadioButtonGroup
        :id="cardXNodeXWidgetData?.node.alias"
        :model-value="initialValue"
        :class="['button-group', flexDirection]"
        tabindex="-1"
        @update:model-value="onUpdateModelValue"
    >
        <div
            v-for="option in options"
            :key="option.key"
            class="radio-options"
        >
            <RadioButton
                :input-id="option.key"
                :value="option.key"
                size="small"
            />
            <label :for="option.key">{{ option.label }}</label>
        </div>
    </RadioButtonGroup>
</template>

<style scoped>
.p-radiobutton {
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

.radio-options {
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
.flex-row > .p-radiobutton,
.flex-column > .p-radiobutton {
    vertical-align: top;
}
</style>
