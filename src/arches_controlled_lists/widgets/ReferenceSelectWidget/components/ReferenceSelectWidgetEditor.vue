<script setup lang="ts">
import { computed, ref, watchEffect } from "vue";

import TreeSelect from "primevue/treeselect";

import { fetchWidgetOptions } from "@/arches_controlled_lists/datatypes/reference-select/api.ts";

import type { Ref } from "vue";
import type { TreeExpandedKeys } from "primevue/tree";

import type {
    ReferenceSelectDatatypeCardXNodeXWidgetData,
    ReferenceSelectDetails,
    ReferenceSelectTreeNode,
    ReferenceSelectValue,
} from "@/arches_controlled_lists/datatypes/reference-select/types.ts";

const { aliasedNodeData, cardXNodeXWidgetData, graphSlug, nodeAlias } =
    defineProps<{
        aliasedNodeData: ReferenceSelectValue;
        cardXNodeXWidgetData: ReferenceSelectDatatypeCardXNodeXWidgetData;
        graphSlug: string;
        nodeAlias: string;
    }>();

const emit = defineEmits<{
    (event: "update:value", updatedValue: ReferenceSelectValue): void;
}>();

const options = ref<ReferenceSelectTreeNode[]>();
const isLoading = ref(false);
const optionsError = ref<string | null>(null);
const expandedKeys: Ref<TreeExpandedKeys> = ref({});

const initialValueFromTileData = computed(() => {
    if (aliasedNodeData?.details) {
        return aliasedNodeData.details.reduce<Record<string, boolean>>(
            (acc, option) => {
                acc[option.list_item_id] = true;
                return acc;
            },
            {},
        );
    }
    return {};
});

watchEffect(() => {
    getOptions();
});

function optionAsNode(item: ReferenceSelectTreeNode): ReferenceSelectTreeNode {
    expandedKeys.value = {
        ...expandedKeys.value,
        [item.list_item_id]: true,
    };
    return {
        key: item.list_item_id,
        label: item.display_value,
        children: item.children?.map(optionAsNode),
        data: item as unknown as ReferenceSelectDetails,
    };
}

function optionsAsNodes(
    items: ReferenceSelectTreeNode[],
): ReferenceSelectTreeNode[] {
    if (items.length > 0) {
        return items.map(optionAsNode);
    }
    return [];
}

async function getOptions() {
    isLoading.value = true;
    try {
        const widgetOptions = await fetchWidgetOptions(graphSlug, nodeAlias);

        options.value = optionsAsNodes(widgetOptions);
    } catch (error) {
        optionsError.value = (error as Error).message;
    } finally {
        isLoading.value = false;
    }
}

function onUpdateModelValue(
    updatedValue: { [key: string]: boolean } | null,
): void {
    if (!updatedValue) {
        emit("update:value", {
            node_value: [],
            display_value: "",
            details: [],
        });

        return;
    }

    const nodeValue = [];
    const details = [];

    for (const updatedListItemId of Object.keys(updatedValue)) {
        const optionsQueue = [...(options.value || [])];
        let selectedOption: ReferenceSelectTreeNode | undefined;

        for (const option of optionsQueue) {
            if (option.key === updatedListItemId) {
                selectedOption = option;
                break;
            }

            if (option.children) {
                optionsQueue.push(...option.children);
            }
        }

        const listId = selectedOption?.data.list_item_values.find(
            (item) => item.list_item_id === updatedListItemId,
        )?.id;

        nodeValue.push({
            list_id: listId!,
            labels: selectedOption!.data.list_item_values,
            uri: selectedOption!.data.uri,
        });
        details.push(selectedOption!.data);
    }

    const displayValue = details.map((item) => item.display_value).join(", ");

    emit("update:value", {
        node_value: nodeValue,
        display_value: displayValue,
        details: details,
    });
}
</script>

<template>
    <TreeSelect
        style="display: flex"
        option-value="list_item_id"
        :fluid="true"
        :loading="isLoading"
        :options="options"
        :expanded-keys="expandedKeys"
        :model-value="initialValueFromTileData"
        :placeholder="cardXNodeXWidgetData.config.placeholder"
        :selection-mode="
            cardXNodeXWidgetData.node.config.multiValue ? 'multiple' : 'single'
        "
        :show-clear="true"
        @update:model-value="onUpdateModelValue($event)"
    />
</template>
