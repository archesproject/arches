<script setup lang="ts">
import { computed, ref, watchEffect } from "vue";

import { useGettext } from "vue3-gettext";

import Select from "primevue/select";

import { fetchRelatableResources } from "@/arches_component_lab/datatypes/resource-instance/api.ts";
import { debounce } from "@/arches_component_lab/utils.ts";

import type { SelectFilterEvent } from "primevue/select";
import type { VirtualScrollerLazyEvent } from "primevue/virtualscroller";

import type {
    ResourceInstanceValue,
    ResourceInstanceDataItem,
    ResourceInstanceSelectOption,
} from "@/arches_component_lab/datatypes/resource-instance/types.ts";

import type { CardXNodeXWidgetData } from "@/arches_component_lab/types";

const {
    cardXNodeXWidgetData,
    nodeAlias,
    graphSlug,
    aliasedNodeData,
    shouldEmitSimplifiedValue,
    defaultTerm,
} = defineProps<{
    cardXNodeXWidgetData: CardXNodeXWidgetData;
    nodeAlias: string;
    graphSlug: string;
    aliasedNodeData: ResourceInstanceValue | null;
    shouldEmitSimplifiedValue?: boolean;
    defaultTerm?: string;
}>();

const emit = defineEmits<{
    (
        event: "update:value",
        updatedValue: ResourceInstanceValue | string[],
    ): void;
}>();

const { $gettext } = useGettext();

const itemSize = 36; // in future iteration this should be declared in the CardXNodeXWidgetData config

const options = ref<{ display_value: string; resource_id: string }[]>(
    aliasedNodeData?.details || [],
);
const isLoading = ref(false);
const resourceResultsPage = ref(0);
const resourceResultsTotalCount = ref(0);
const fetchError = ref<string | null>(null);
const emptyFilterMessage = ref($gettext("Search returned no results"));

const resourceResultsCurrentCount = computed(() => options.value.length);

watchEffect(() => {
    getOptions(1);
});

const onFilter = debounce((event: SelectFilterEvent) => {
    getOptions(1, event.value);
}, 600);

async function getOptions(page: number, filterTerm?: string) {
    try {
        isLoading.value = true;
        emptyFilterMessage.value = $gettext("Searching...");
        const filterTerms = [];
        if (defaultTerm) {
            filterTerms.push(defaultTerm);
        }
        if (filterTerm) {
            filterTerms.push(filterTerm);
        }
        const resourceData = await fetchRelatableResources(
            graphSlug,
            nodeAlias,
            page,
            filterTerms,
            aliasedNodeData?.details?.[0]?.resource_id,
        );

        const references = resourceData.data.map(
            (
                resourceRecord: ResourceInstanceDataItem,
            ): ResourceInstanceSelectOption => ({
                display_value: resourceRecord.display_value ?? "",
                resource_id: resourceRecord.resourceinstanceid,
            }),
        );

        if (resourceData.current_page == 1) {
            options.value = references;
        } else {
            options.value = [...options.value, ...references];
        }

        resourceResultsPage.value = resourceData.current_page;
        resourceResultsTotalCount.value = resourceData.total_results;
    } catch (error) {
        fetchError.value = (error as Error).message;
    } finally {
        isLoading.value = false;
        if (
            options.value.length - (aliasedNodeData?.details?.length ?? 0) ==
            0
        ) {
            emptyFilterMessage.value = $gettext("Search returned no results");
        }
    }
}

async function onLazyLoadResources(event?: VirtualScrollerLazyEvent) {
    if (isLoading.value) {
        return;
    }

    if (
        // if we have already fetched all the resources
        resourceResultsTotalCount.value > 0 &&
        resourceResultsCurrentCount.value >= resourceResultsTotalCount.value
    ) {
        return;
    }

    if (
        // if the user has NOT scrolled to the end of the list
        event &&
        event.last < resourceResultsCurrentCount.value - 1
    ) {
        return;
    }

    if (
        // if the dropdown is opened and we already have data
        !event &&
        resourceResultsCurrentCount.value > 0
    ) {
        return;
    }

    await getOptions((resourceResultsPage.value || 0) + 1);
}

function getOption(value: string): ResourceInstanceSelectOption | undefined {
    return options.value.find((option) => option.resource_id == value);
}

function onUpdateModelValue(updatedValue: string | null) {
    const selectedValue = updatedValue ?? "";

    const option = getOption(selectedValue);

    if (shouldEmitSimplifiedValue) {
        if (updatedValue === null) {
            emit("update:value", []);
        } else {
            emit("update:value", [selectedValue]);
        }
        return;
    } else {
        emit("update:value", {
            display_value: option ? option.display_value : "",
            node_value: updatedValue
                ? {
                      inverseOntologyProperty: "",
                      ontologyProperty: "",
                      resourceId: selectedValue,
                      resourceXresourceId: "",
                  }
                : null,
            details: option ? [option] : [],
        } as ResourceInstanceValue);
    }
}
</script>

<template>
    <Select
        display="chip"
        option-label="display_value"
        option-value="resource_id"
        :filter="true"
        :filter-fields="['display_value', 'resource_id']"
        :empty-filter-message="emptyFilterMessage"
        :filter-placeholder="$gettext('Filter Resources')"
        :fluid="true"
        :label-id="cardXNodeXWidgetData.node.alias"
        :loading="isLoading"
        :model-value="aliasedNodeData?.details?.[0]?.resource_id"
        :options="options"
        :placeholder="cardXNodeXWidgetData.config.placeholder"
        :reset-filter-on-hide="true"
        :show-clear="true"
        :virtual-scroller-options="{
            itemSize: itemSize,
            lazy: true,
            loading: isLoading,
            onLazyLoad: onLazyLoadResources,
        }"
        @filter="onFilter"
        @before-show="getOptions(1)"
        @update:model-value="onUpdateModelValue($event)"
    />
</template>
