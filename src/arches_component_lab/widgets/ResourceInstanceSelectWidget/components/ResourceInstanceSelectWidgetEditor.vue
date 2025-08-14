<script setup lang="ts">
import { computed, ref, watchEffect } from "vue";

import { useGettext } from "vue3-gettext";

import Select from "primevue/select";

import { fetchRelatableResources } from "@/arches_component_lab/datatypes/resource-instance/api.ts";

import type { SelectFilterEvent } from "primevue/select";
import type { VirtualScrollerLazyEvent } from "primevue/virtualscroller";

import type { CardXNodeXWidgetData } from "@/arches_component_lab/types";
import type {
    ResourceInstanceReference,
    ResourceInstanceResult,
    ResourceInstanceValue,
} from "@/arches_component_lab/datatypes/resource-instance/types.ts";

const { $gettext } = useGettext();

const { cardXNodeXWidgetData, nodeAlias, graphSlug, value } = defineProps<{
    cardXNodeXWidgetData: CardXNodeXWidgetData;
    nodeAlias: string;
    graphSlug: string;
    value: ResourceInstanceValue;
}>();

const emit = defineEmits<{
    (event: "update:value", updatedValue: ResourceInstanceValue): void;
}>();

const itemSize = 36; // in future iteration this should be declared in the CardXNodeXWidgetData config

const options = ref<ResourceInstanceReference[]>([]);
const isLoading = ref(false);
const resourceResultsPage = ref(0);
const resourceResultsTotalCount = ref(0);
const fetchError = ref<string | null>(null);

const resourceResultsCurrentCount = computed(() => options.value.length);

watchEffect(() => {
    getOptions(1);
});

async function getOptions(page: number, filterTerm?: string) {
    try {
        isLoading.value = true;

        const resourceData = await fetchRelatableResources(
            graphSlug,
            nodeAlias,
            page,
            filterTerm,
            value?.details?.[0]?.resource_id,
        );

        const references = resourceData.data.map(
            (
                resourceRecord: ResourceInstanceResult,
            ): ResourceInstanceReference => ({
                display_value: resourceRecord.display_value,
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
    }
}

function getOption(value: string): ResourceInstanceReference | undefined {
    return options.value.find((option) => option.resource_id == value);
}

function onFilter(event: SelectFilterEvent) {
    if (value?.details) {
        options.value = value.details;
    } else {
        options.value = [];
    }

    getOptions(1, event.value);
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

function onUpdateModelValue(updatedValue: string | null) {
    const option = getOption(updatedValue!);

    emit("update:value", {
        display_value: option ? option.display_value : "",
        node_value: {
            inverseOntologyProperty: "",
            ontologyProperty: "",
            resourceId: updatedValue ?? "",
            resourceXresourceId: "",
        },
        details: option ? [option] : [],
    });
}
</script>

<template>
    <Select
        display="chip"
        option-label="display_value"
        option-value="resource_id"
        :filter="true"
        :filter-placeholder="$gettext('Filter Resources')"
        :fluid="true"
        :label-id="cardXNodeXWidgetData.node.alias"
        :loading="isLoading"
        :model-value="value?.details?.[0]?.resource_id"
        :options="options"
        :placeholder="$gettext('Select Resources')"
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
