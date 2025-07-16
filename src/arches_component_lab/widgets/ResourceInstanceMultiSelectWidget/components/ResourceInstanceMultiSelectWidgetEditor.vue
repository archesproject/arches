<script setup lang="ts">
import { computed, ref, watchEffect } from "vue";

import arches from "arches";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";
import MultiSelect from "primevue/multiselect";

import GenericFormField from "@/arches_component_lab/generic/GenericFormField.vue";

import { fetchRelatableResources } from "@/arches_component_lab/widgets/api.ts";

import type { FormFieldResolverOptions } from "@primevue/forms";
import type { MultiSelectFilterEvent } from "primevue/multiselect";
import type { VirtualScrollerLazyEvent } from "primevue/virtualscroller";

import type { NodeData } from "@/arches_component_lab/types.ts";
import type {
    ResourceInstanceReference,
    ResourceInstanceResult,
} from "@/arches_component_lab/widgets/types.ts";

const { nodeAlias, graphSlug, value } = defineProps<{
    nodeAlias: string;
    graphSlug: string;
    value: NodeData | null | undefined;
}>();

const { $gettext } = useGettext();

const itemSize = 36; // in future iteration this should be declared in the CardXNodeXWidget config

const options = ref<ResourceInstanceReference[]>([]);
const isLoading = ref(false);
const resourceResultsPage = ref(0);
const resourceResultsTotalCount = ref(0);
const fetchError = ref<string | null>(null);

const resourceResultsCurrentCount = computed(() => options.value.length);

const initialValueFromTileData = computed(() => {
    if (value?.interchange_value) {
        return (value.interchange_value as ResourceInstanceReference[]).map(
            (option) => {
                return option.resource_id;
            },
        );
    }
    return [];
});

watchEffect(() => {
    getOptions(1);
});

function onFilter(event: MultiSelectFilterEvent) {
    if (value?.interchange_value) {
        options.value = value.interchange_value as ResourceInstanceReference[];
    } else {
        options.value = [];
    }

    getOptions(1, event.value);
}

async function getOptions(page: number, filterTerm?: string) {
    try {
        isLoading.value = true;

        const resourceData = await fetchRelatableResources(
            graphSlug,
            nodeAlias,
            page,
            filterTerm,
            value?.interchange_value as ResourceInstanceReference[],
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

function resolver(event: FormFieldResolverOptions) {
    return event.value.map((resourceId: string) => {
        return getOption(resourceId);
    });
}
</script>

<template>
    <GenericFormField
        v-bind="$attrs"
        :node-alias="nodeAlias"
        :initial-value="initialValueFromTileData"
        :resolver="resolver"
    >
        <MultiSelect
            display="chip"
            option-label="display_value"
            option-value="resource_id"
            :filter="true"
            :filter-placeholder="$gettext('Filter Resources')"
            :fluid="true"
            :loading="isLoading"
            :options="options"
            :placeholder="$gettext('Select Resources')"
            :reset-filter-on-hide="true"
            :virtual-scroller-options="{
                itemSize: itemSize,
                lazy: true,
                loading: isLoading,
                onLazyLoad: onLazyLoadResources,
            }"
            @filter="onFilter"
            @before-show="getOptions(1)"
        >
            <template #chip="slotProps">
                <div style="width: 100%">
                    <div class="chip-text">
                        {{ getOption(slotProps.value)?.display_value }}
                    </div>
                </div>
                <div class="button-container">
                    <Button
                        as="a"
                        icon="pi pi-info-circle"
                        target="_blank"
                        variant="text"
                        size="small"
                        style="text-decoration: none"
                        :href="`${arches.urls.resource_report}${slotProps.value}`"
                        @click.stop
                    />
                    <Button
                        as="a"
                        icon="pi pi-pencil"
                        target="_blank"
                        variant="text"
                        size="small"
                        style="text-decoration: none"
                        :href="`${arches.urls.resource_editor}${slotProps.value}`"
                        @click.stop
                    />
                    <Button
                        icon="pi pi-times"
                        variant="text"
                        size="small"
                        @click.stop="
                            slotProps.removeCallback($event, slotProps.value)
                        "
                    />
                </div>
            </template>
        </MultiSelect>
    </GenericFormField>
</template>

<style scoped>
.button-container {
    display: flex;
    justify-content: flex-end;
}

.chip-text {
    width: min-content;
    min-width: fit-content;
    overflow-wrap: anywhere;
    padding: 0.5rem 1rem;
}

:deep(.p-multiselect-label) {
    width: inherit;
    flex-direction: column;
    white-space: break-spaces;
    align-items: flex-start;
}

:deep(.p-multiselect-chip-item) {
    width: inherit;
    border: 0.125rem solid var(--p-inputtext-border-color);
    padding: 0.25rem;
    border-radius: 0.5rem;
    margin: 0.25rem;
}

:deep(.p-multiselect-label-container) {
    white-space: break-spaces;
    width: inherit;
}
</style>
