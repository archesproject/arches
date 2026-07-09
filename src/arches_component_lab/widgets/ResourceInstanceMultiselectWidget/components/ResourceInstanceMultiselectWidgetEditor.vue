<script setup lang="ts">
import { computed, ref, watch, watchEffect } from "vue";

import arches from "arches";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";
import MultiSelect from "primevue/multiselect";

import ResourceInstanceCreation from "@/arches_component_lab/widgets/components/ResourceInstanceCreation.vue";

import { fetchRelatableResources } from "@/arches_component_lab/datatypes/resource-instance-list/api.ts";
import { buildResourceInstanceListAliasedNodeData } from "@/arches_component_lab/datatypes/resource-instance-list/utils.ts";
import { debounce } from "@/arches_component_lab/utils.ts";

import type { MultiSelectFilterEvent } from "primevue/multiselect";
import type { VirtualScrollerLazyEvent } from "primevue/virtualscroller";

import type {
    ResourceInstanceDataItem,
    ResourceInstanceListOption,
    ResourceInstanceListCardXNodeXWidgetData,
} from "@/arches_component_lab/datatypes/resource-instance-list/types.ts";
import type { AliasedTileData } from "@/arches_component_lab/types.ts";
import type { ResourceInstanceListAliasedNodeData } from "@/arches_component_lab/datatypes/resource-instance-list/types.ts";

const ITEM_SIZE = 36;

const { cardXNodeXWidgetData, nodeAlias, graphSlug, aliasedNodeData } =
    defineProps<{
        cardXNodeXWidgetData?: ResourceInstanceListCardXNodeXWidgetData;
        nodeAlias?: string;
        graphSlug?: string;
        aliasedNodeData?: ResourceInstanceListAliasedNodeData | null;
    }>();

const emit = defineEmits<{
    (event: "update:isLoading", isLoading: boolean): void;
    (
        event: "update:aliasedNodeData",
        updatedValue: ResourceInstanceListAliasedNodeData,
    ): void;
    (
        event: "initialized",
        updatedValue: ResourceInstanceListAliasedNodeData,
    ): void;
}>();

const { $gettext } = useGettext();

const options = ref<ResourceInstanceListOption[]>([]);
const isLoading = ref(false);
const resourceResultsPage = ref(0);
const resourceResultsTotalCount = ref(0);
const fetchError = ref<string | null>(null);
const emptyFilterMessage = ref($gettext("Search returned no results"));

const selectedGraphId = ref<string>("");
const showResourceCreation = ref(false);
const resourceCreationDialogKey = ref(0);

const selectedValues = ref<string[]>(
    aliasedNodeData?.node_value
        ?.map(
            (resourceReference) =>
                resourceReference.resourceId ??
                (
                    resourceReference as unknown as {
                        resourceinstanceid?: string;
                    }
                ).resourceinstanceid,
        )
        .filter(
            (resourceId): resourceId is string => resourceId !== undefined,
        ) ?? [],
);

const resourceResultsCurrentCount = computed(() => options.value.length);
const hasInitialized = ref(false);

watch(isLoading, (newValue) => {
    emit("update:isLoading", newValue);
});

watchEffect(() => {
    getOptions(1);
});

async function getOptions(page: number, filterTerm?: string) {
    if (!graphSlug || !nodeAlias) return;
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
        if (options.value.length === 0) {
            emptyFilterMessage.value = $gettext("Search returned no results");
        }
        if (page === 1 && !hasInitialized.value) {
            hasInitialized.value = true;
            const resolvedOptions = selectedValues.value
                .map((selectedId) =>
                    options.value.find(
                        (option) => option.resource_id === selectedId,
                    ),
                )
                .filter(
                    (option): option is ResourceInstanceListOption =>
                        option !== undefined,
                );
            const nodeValues = selectedValues.value.map((selectedId) => ({
                inverseOntologyProperty: "",
                ontologyProperty: "",
                resourceId: selectedId,
                resourceXresourceId: "",
            }));
            emit(
                "initialized",
                aliasedNodeData ??
                    buildResourceInstanceListAliasedNodeData(
                        nodeValues,
                        resolvedOptions,
                    ),
            );
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

const onFilter = debounce(function onFilterDebounced(
    event: MultiSelectFilterEvent,
) {
    getOptions(1, event.value);
}, 600);

function onCreateNewResource(graphId: string) {
    selectedGraphId.value = graphId;
    resourceCreationDialogKey.value++;
    showResourceCreation.value = true;
}

function onUpdateModelValue(updatedValue: string[]) {
    selectedValues.value = updatedValue;
    const nodeValues = updatedValue.map((selectedId) => ({
        inverseOntologyProperty: "",
        ontologyProperty: "",
        resourceId: selectedId,
        resourceXresourceId: "",
    }));
    const resolvedOptions = updatedValue
        .map((selectedId) =>
            options.value.find((option) => option.resource_id === selectedId),
        )
        .filter(
            (option): option is ResourceInstanceListOption =>
                option !== undefined,
        );
    emit(
        "update:aliasedNodeData",
        buildResourceInstanceListAliasedNodeData(nodeValues, resolvedOptions),
    );
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
        :input-id="cardXNodeXWidgetData?.node.alias"
        :loading="isLoading"
        :model-value="selectedValues"
        :options="options"
        :placeholder="cardXNodeXWidgetData?.config.placeholder"
        :reset-filter-on-hide="true"
        :virtual-scroller-options="{
            itemSize: ITEM_SIZE,
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
            v-if="cardXNodeXWidgetData?.node.config.graphs?.length"
            #header
        >
            <div class="create-new-options-header">
                <div
                    v-for="graph in cardXNodeXWidgetData?.node.config.graphs"
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
                    class="no-text-decoration"
                    :href="`${arches.urls.resource_report}${slotProps.value}`"
                    @click.stop
                />
                <Button
                    as="a"
                    icon="pi pi-pencil"
                    target="_blank"
                    variant="text"
                    size="small"
                    class="no-text-decoration"
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
.no-text-decoration {
    text-decoration: none;
}

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
