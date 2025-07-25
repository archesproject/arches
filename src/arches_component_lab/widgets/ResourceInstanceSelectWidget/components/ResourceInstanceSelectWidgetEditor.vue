<script setup lang="ts">
import { computed, ref, watchEffect } from "vue";

import { useGettext } from "vue3-gettext";

import Select from "primevue/select";

import GenericFormField from "@/arches_component_lab/generics/GenericFormField.vue";

import { fetchRelatableResources } from "@/arches_component_lab/datatypes/resource-instance/api.ts";

import type { FormFieldResolverOptions } from "@primevue/forms";
import type { SelectFilterEvent } from "primevue/select";
import type { VirtualScrollerLazyEvent } from "primevue/virtualscroller";

import type {
    ResourceInstanceReference,
    ResourceInstanceResult,
    ResourceInstanceValue,
} from "@/arches_component_lab/datatypes/resource-instance/types.ts";

const props = defineProps<{
    nodeAlias: string;
    graphSlug: string;
    value: ResourceInstanceValue;
}>();

const { $gettext } = useGettext();

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

function onFilter(event: SelectFilterEvent) {
    if (props.value?.details) {
        options.value = props.value.details;
    } else {
        options.value = [];
    }

    getOptions(1, event.value);
}

async function getOptions(page: number, filterTerm?: string) {
    try {
        isLoading.value = true;

        const resourceData = await fetchRelatableResources(
            props.graphSlug,
            props.nodeAlias,
            page,
            filterTerm,
            props.value?.details?.[0]?.resource_id,
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

function getOption(value: string): ResourceInstanceReference | undefined {
    return options.value.find((option) => option.resource_id == value);
}

function transformValueForForm(event: FormFieldResolverOptions) {
    const option = getOption(event.value);

    return {
        display_value: option ? option.display_value : "",
        node_value: event.value ? [event.value] : [],
        details: option ? [option] : [],
    };
}
</script>

<template>
    <GenericFormField
        v-bind="$attrs"
        :node-alias="nodeAlias"
        :transform-value-for-form="transformValueForForm"
    >
        <Select
            display="chip"
            option-label="display_value"
            option-value="resource_id"
            :filter="true"
            :filter-placeholder="$gettext('Filter Resources')"
            :fluid="true"
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
        />
    </GenericFormField>
</template>
