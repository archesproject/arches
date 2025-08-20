<script setup lang="ts">
import { computed, ref, watchEffect } from "vue";

import arches from "arches";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";
import MultiSelect from "primevue/multiselect";

import { fetchRelatableResources } from "@/arches_component_lab/datatypes/resource-instance-list/api.ts";

import type { MultiSelectFilterEvent } from "primevue/multiselect";
import type { VirtualScrollerLazyEvent } from "primevue/virtualscroller";

import type {
    ResourceInstanceListValue,
    ResourceInstanceReference,
} from "@/arches_component_lab/datatypes/resource-instance-list/types";
import type {
    ResourceInstanceListOption,
    ResourceInstanceDataItem,
} from "@/arches_component_lab/datatypes/resource-instance-list/types.ts";
import type { CardXNodeXWidgetData } from "@/arches_component_lab/types.ts";

const { cardXNodeXWidgetData, nodeAlias, graphSlug, aliasedNodeData } =
    defineProps<{
        cardXNodeXWidgetData: CardXNodeXWidgetData;
        nodeAlias: string;
        graphSlug: string;
        aliasedNodeData: ResourceInstanceListValue;
    }>();

const emit = defineEmits<{
    (event: "update:value", updatedValue: ResourceInstanceListValue): void;
}>();

const { $gettext } = useGettext();

const itemSize = 36; // in future iteration this should be declared in the CardXNodeXWidgetData config

const options = ref<ResourceInstanceListOption[]>([]);
const isLoading = ref(false);
const resourceResultsPage = ref(0);
const resourceResultsTotalCount = ref(0);
const fetchError = ref<string | null>(null);

const resourceResultsCurrentCount = computed(() => options.value.length);

const initialValueFromTileData = computed(() => {
    if (aliasedNodeData?.details) {
        return aliasedNodeData.details.map((option) => {
            return option.resource_id;
        });
    }
    return [];
});

watchEffect(() => {
    getOptions(1);
});

function onFilter(event: MultiSelectFilterEvent) {
    if (aliasedNodeData?.details) {
        options.value = aliasedNodeData.details;
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
            aliasedNodeData?.details,
        );

        const references = resourceData.data.map(
            (
                resourceRecord: ResourceInstanceDataItem,
            ): ResourceInstanceListOption => ({
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

function getOption(value: string): {
    display_value: string;
    resource_id: string;
} {
    return options.value.find((option) => option.resource_id == value)!;
}

function onUpdateModelValue(updatedValue: string[]) {
    const options = updatedValue.map((resourceId: string) => {
        return getOption(resourceId);
    });

    const formattedNodeValues: ResourceInstanceReference[] = updatedValue.map(
        (value) => {
            return {
                inverseOntologyProperty: "",
                ontologyProperty: "",
                resourceId: value ?? "",
                resourceXresourceId: "",
            } as ResourceInstanceReference;
        },
    );

    const formattedValue = {
        display_value: options
            .map((option) => option?.display_value)
            .join(", "),
        node_value: formattedNodeValues,
        details: options ?? [],
    };

    emit("update:value", formattedValue);
}
</script>

<template>
    <MultiSelect
        display="chip"
        option-label="display_value"
        option-value="resource_id"
        :filter="true"
        :filter-placeholder="$gettext('Filter Resources')"
        :fluid="true"
        :input-id="cardXNodeXWidgetData.node.alias"
        :loading="isLoading"
        :model-value="initialValueFromTileData"
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
        @update:model-value="onUpdateModelValue($event)"
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
    display: flex;
}

:deep(.p-multiselect-label-container) {
    white-space: break-spaces;
    width: inherit;
}
</style>
