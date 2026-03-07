<script setup lang="ts">
import { computed, ref, watchEffect } from "vue";

import arches from "arches";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";
import MultiSelect from "primevue/multiselect";

import ResourceInstanceCreation from "@/arches_component_lab/widgets/components/ResourceInstanceCreation.vue";

import { fetchRelatableResources } from "@/arches_component_lab/datatypes/resource-instance-list/api.ts";
import { debounce } from "@/arches_component_lab/utils.ts";

import type { MultiSelectFilterEvent } from "primevue/multiselect";
import type { VirtualScrollerLazyEvent } from "primevue/virtualscroller";

import type {
    ResourceInstanceListValue,
    ResourceInstanceReference,
} from "@/arches_component_lab/datatypes/resource-instance-list/types";
import type {
    ResourceInstanceDataItem,
    ResourceInstanceListOption,
    ResourceInstanceListCardXNodeXWidgetData,
} from "@/arches_component_lab/datatypes/resource-instance-list/types.ts";
import type { AliasedTileData } from "@/arches_component_lab/types.ts";

const {
    cardXNodeXWidgetData,
    nodeAlias,
    graphSlug,
    aliasedNodeData,
    shouldEmitSimplifiedValue,
} = defineProps<{
    cardXNodeXWidgetData: ResourceInstanceListCardXNodeXWidgetData;
    nodeAlias: string;
    graphSlug: string;
    aliasedNodeData: ResourceInstanceListValue | null;
    shouldEmitSimplifiedValue?: boolean;
}>();

const emit = defineEmits<{
    (
        event: "update:value",
        updatedValue: ResourceInstanceListValue | string[],
    ): void;
}>();

const { $gettext } = useGettext();

// in future iteration these may be declared in the CardXNodeXWidgetData config
const itemSize = 36;

const options = ref<ResourceInstanceListOption[]>(
    aliasedNodeData?.details ?? [],
);
const isLoading = ref(false);
const resourceResultsPage = ref(0);
const resourceResultsTotalCount = ref(0);
const fetchError = ref<string | null>(null);
const emptyFilterMessage = ref($gettext("Search returned no results"));

const selectedGraphId = ref<string>("");
const showResourceCreation = ref(false);
const resourceCreationDialogKey = ref(0);

const resourceResultsCurrentCount = computed(() => options.value.length);
const selectedValues = ref<string[]>(
    aliasedNodeData?.details?.map((option) => option.resource_id) || [],
);

watchEffect(() => {
    getOptions(1);
});

const onFilter = debounce((event: MultiSelectFilterEvent) => {
    getOptions(1, event.value);
}, 600);

async function getOptions(page: number, filterTerm?: string) {
    try {
        isLoading.value = true;
        emptyFilterMessage.value = $gettext("Searching...");

        const resourceData = await fetchRelatableResources(
            graphSlug,
            nodeAlias,
            page,
            filterTerm,
            selectedValues.value,
        );

        const references = resourceData.data.map(
            (
                resourceRecord: ResourceInstanceDataItem,
            ): ResourceInstanceListOption => ({
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

function getOption(value: string): ResourceInstanceListOption | undefined {
    return options.value.find((option) => option.resource_id == value);
}

function onCreateNewResource(graphId: string) {
    selectedGraphId.value = graphId;
    resourceCreationDialogKey.value++;
    showResourceCreation.value = true;
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

    selectedValues.value = updatedValue;

    if (shouldEmitSimplifiedValue) {
        emit("update:value", updatedValue as string[]);
    } else {
        const formattedValue = {
            display_value: options
                .map((option) => option?.display_value)
                .join(", "),
            node_value: formattedNodeValues,
            details: options ?? [],
        } as ResourceInstanceListValue;

        emit("update:value", formattedValue);
    }
}

async function onResourceCreated(createdTile: AliasedTileData) {
    selectedValues.value = [
        ...selectedValues.value,
        createdTile.resourceinstance,
    ];
    getOptions(1);
    onUpdateModelValue(selectedValues.value);
    showResourceCreation.value = false;
}
</script>

<template>
    <MultiSelect
        display="chip"
        option-label="display_value"
        option-value="resource_id"
        :filter="true"
        :filter-fields="['display_value', 'resource_id']"
        :empty-filter-message="emptyFilterMessage"
        :filter-placeholder="$gettext('Filter Resources')"
        :fluid="true"
        :input-id="cardXNodeXWidgetData.node.alias"
        :loading="isLoading"
        :model-value="selectedValues"
        :options="options"
        :placeholder="cardXNodeXWidgetData.config.placeholder"
        :reset-filter-on-hide="true"
        :virtual-scroller-options="{
            itemSize: itemSize,
            lazy: true,
            loading: isLoading,
            onLazyLoad: onLazyLoadResources,
        }"
        :overlay-visible="showResourceCreation ? false : undefined"
        @filter="onFilter"
        @before-show="getOptions(1)"
        @update:model-value="onUpdateModelValue($event)"
    >
        <template
            v-if="cardXNodeXWidgetData.node.config.graphs?.length"
            #header
        >
            <div class="create-new-options-header">
                <div
                    v-for="graph in cardXNodeXWidgetData.node.config.graphs"
                    :key="graph.graphid"
                    class="create-new-option"
                    @click="onCreateNewResource(graph.graphid)"
                >
                    {{
                        $gettext("Create a new %{graphName}", {
                            graphName: graph.name,
                        })
                    }}
                </div>
            </div>
        </template>
        <template #option="slotProps">
            <div>{{ slotProps.option.display_value }}</div>
        </template>
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

    <ResourceInstanceCreation
        v-if="showResourceCreation"
        :key="resourceCreationDialogKey"
        :graph-id="selectedGraphId!"
        @resource-created="onResourceCreated"
    />
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

<style>
.p-multiselect-overlay {
    display: flex;
    flex-direction: column;
}

.p-multiselect-header {
    order: 0;
}

.create-new-options-header {
    order: 1;
}

.p-multiselect-list-container,
.p-virtualscroller {
    order: 2;
}

.create-new-option {
    font-weight: bold;
    padding: 0.5rem 1rem;
    cursor: pointer;
}

.create-new-option:hover {
    background: var(--p-multiselect-option-focus-background);
}
</style>
