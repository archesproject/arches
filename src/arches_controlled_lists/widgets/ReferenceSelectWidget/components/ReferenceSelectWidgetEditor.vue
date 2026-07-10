<script setup lang="ts">
import { computed, onMounted, ref, watch, watchEffect } from "vue";

import { useGettext } from "vue3-gettext";
import TreeSelect from "primevue/treeselect";

import { useReferenceSelectOptionsStore } from "@/arches_controlled_lists/stores/useReferenceSelectOptionsStore.ts";
import { buildReferenceSelectAliasedNodeData } from "@/arches_controlled_lists/datatypes/reference-select/utils.ts";

import type { Ref } from "vue";
import type { TreeExpandedKeys } from "primevue/tree";

import type { ReferenceSelectAliasedNodeData } from "@/arches_controlled_lists/datatypes/reference-select/types.ts";
import type {
    ReferenceSelectDatatypeCardXNodeXWidgetData,
    ReferenceSelectDetails,
    ReferenceSelectTreeNode,
    ReferenceSelectNodeValue,
} from "@/arches_controlled_lists/datatypes/reference-select/types.ts";

const {
    aliasedNodeData,
    cardXNodeXWidgetData,
    graphSlug,
    nodeAlias,
    systemLanguageCode,
} = defineProps<{
    aliasedNodeData: ReferenceSelectAliasedNodeData | null;
    cardXNodeXWidgetData?: ReferenceSelectDatatypeCardXNodeXWidgetData;
    graphSlug?: string;
    nodeAlias?: string;
    systemLanguageCode: string;
}>();

const emit = defineEmits<{
    (event: "update:isLoading", updatedValue: boolean): void;
    (event: "update:value", updatedValue: ReferenceSelectNodeValue[]): void;
    (
        event: "update:aliasedNodeData",
        updatedValue: ReferenceSelectAliasedNodeData,
    ): void;
    (event: "initialized", updatedValue: ReferenceSelectAliasedNodeData): void;
}>();

const { current: preferredLanguageCode } = useGettext();

const options = ref<ReferenceSelectTreeNode[]>();
const isLoading = ref(false);
const optionsError = ref<string | null>(null);
const expandedKeys: Ref<TreeExpandedKeys> = ref({});

const initialValueFromTileData = computed(() => {
    if (aliasedNodeData?.node_value?.length) {
        return aliasedNodeData.node_value.reduce<Record<string, boolean>>(
            (accumulator, item) => {
                const listItemId = item.labels?.[0]?.list_item_id;
                if (listItemId) {
                    accumulator[listItemId] = true;
                }
                return accumulator;
            },
            {},
        );
    }

    const defaultValueFromWidgetConfig = cardXNodeXWidgetData?.config
        ?.defaultValue as ReferenceSelectNodeValue[] | undefined;

    if (
        !defaultValueFromWidgetConfig ||
        defaultValueFromWidgetConfig.length === 0
    ) {
        return undefined;
    }

    return defaultValueFromWidgetConfig?.reduce<Record<string, boolean>>(
        (accumulator, defaultValueItem) => {
            const listItemIdentifier =
                defaultValueItem?.labels?.[0]?.list_item_id;

            if (listItemIdentifier) {
                accumulator[listItemIdentifier] = true;
            }

            return accumulator;
        },
        {},
    );
});

onMounted(() => {
    emit(
        "initialized",
        aliasedNodeData ??
            buildReferenceSelectAliasedNodeData(
                null,
                preferredLanguageCode,
                systemLanguageCode,
            ),
    );
});

watchEffect(() => {
    getOptions();
});

watch(isLoading, (newValue) => {
    emit("update:isLoading", newValue);
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
    if (!graphSlug || !nodeAlias) return;
    isLoading.value = true;
    try {
        const widgetOptions =
            await useReferenceSelectOptionsStore().fetchWidgetOptions(
                graphSlug,
                nodeAlias,
            );

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
        emit("update:value", []);
        emit(
            "update:aliasedNodeData",
            buildReferenceSelectAliasedNodeData(
                null,
                preferredLanguageCode,
                systemLanguageCode,
            ),
        );
        return;
    }

    const nodeValue: ReferenceSelectNodeValue[] = [];

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
    }

    emit("update:value", nodeValue);
    emit(
        "update:aliasedNodeData",
        buildReferenceSelectAliasedNodeData(
            nodeValue,
            preferredLanguageCode,
            systemLanguageCode,
        ),
    );
}
</script>

<template>
    <TreeSelect
        style="display: flex"
        option-value="list_item_id"
        :input-id="nodeAlias"
        :fluid="true"
        :loading="isLoading"
        :options="options"
        :expanded-keys="expandedKeys"
        :model-value="initialValueFromTileData"
        :placeholder="cardXNodeXWidgetData?.config.placeholder"
        :selection-mode="
            cardXNodeXWidgetData?.node.config.multiValue ? 'multiple' : 'single'
        "
        :show-clear="true"
        @update:model-value="onUpdateModelValue($event)"
    />
</template>
