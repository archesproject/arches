<script setup lang="ts">
import { computed, ref, watch, watchEffect } from "vue";

import { useGettext } from "vue3-gettext";

import Button from "openvue/button";
import MultiSelect from "openvue/multiselect";

import { generateArchesURL } from "@/arches_vue_components/application/generate-arches-url.ts";
import ResourceInstanceCreation from "@/arches_vue_components/widgets/components/ResourceInstanceCreation.vue";

import { fetchRelatableResources } from "@/arches_vue_components/datatypes/resource-instance-list/api.ts";
import { buildResourceInstanceListAliasedNodeData } from "@/arches_vue_components/datatypes/resource-instance-list/utils.ts";
import { debounce } from "@/arches_vue_components/utils.ts";

import type { MultiSelectFilterEvent } from "openvue/multiselect";
import type { VirtualScrollerLazyEvent } from "openvue/virtualscroller";

import type {
    ResourceInstanceDataItem,
    ResourceInstanceListOption,
    ResourceInstanceListCardXNodeXWidgetData,
    ResourceInstanceReference,
} from "@/arches_vue_components/datatypes/resource-instance-list/types.ts";
import type { AliasedTileData } from "@/arches_vue_components/types.ts";
import type { ResourceInstanceListAliasedNodeData } from "@/arches_vue_components/datatypes/resource-instance-list/types.ts";

const ITEM_SIZE = 36;
const FILTER_DEBOUNCE_MILLISECONDS = 600;
const UPDATE_IS_LOADING_EVENT = "update:isLoading" as const;
const UPDATE_ALIASED_NODE_DATA_EVENT = "update:aliasedNodeData" as const;
const READY_EVENT = "ready" as const;

const {
    cardXNodeXWidgetData = undefined,
    nodeAlias = undefined,
    graphSlug = undefined,
    aliasedNodeData = null,
} = defineProps<{
    cardXNodeXWidgetData?: ResourceInstanceListCardXNodeXWidgetData;
    nodeAlias?: string;
    graphSlug?: string;
    aliasedNodeData?: ResourceInstanceListAliasedNodeData | null;
}>();

const emit = defineEmits<{
    (event: typeof UPDATE_IS_LOADING_EVENT, isLoading: boolean): void;
    (
        event: typeof UPDATE_ALIASED_NODE_DATA_EVENT,
        updatedValue: ResourceInstanceListAliasedNodeData,
    ): void;
    (event: typeof READY_EVENT): void;
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
const unavailableValues = ref<string[]>([]);

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

watch(isLoading, (newValue) => {
    emit(UPDATE_IS_LOADING_EVENT, newValue);
});

watchEffect(async () => {
    if (!graphSlug || !nodeAlias) {
        return;
    }
    await getOptions(1);
    emit(READY_EVENT);
});

async function getOptions(page: number, filterTerm?: string): Promise<void> {
    if (!graphSlug || !nodeAlias) {
        return;
    }
    try {
        isLoading.value = true;
        emptyFilterMessage.value = $gettext("Searching...");

        const requestedValues = [...selectedValues.value];
        const resourceData = await fetchRelatableResources(
            graphSlug,
            nodeAlias,
            page,
            filterTerm,
            requestedValues,
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
            unavailableValues.value = requestedValues.filter((requestedId) =>
                references.every(
                    (reference: ResourceInstanceListOption) =>
                        reference.resource_id !== requestedId,
                ),
            );
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
    }
}

async function onLazyLoadResources(
    event?: VirtualScrollerLazyEvent,
): Promise<void> {
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

function isUnavailable(value: string): boolean {
    return unavailableValues.value.includes(value);
}

function getChipLabel(value: string): string {
    if (isUnavailable(value)) {
        return $gettext("Unavailable resource");
    }
    return getOption(value)?.display_value ?? "";
}

const onFilter = debounce(function onFilterDebounced(
    event: MultiSelectFilterEvent,
): void {
    getOptions(1, event.value);
}, FILTER_DEBOUNCE_MILLISECONDS);

function onCreateNewResource(graphId: string): void {
    selectedGraphId.value = graphId;
    resourceCreationDialogKey.value++;
    showResourceCreation.value = true;
}

function onUpdateModelValue(updatedValue: string[]): void {
    const mergedValue = [...updatedValue];
    selectedValues.value.forEach((selectedId, index) => {
        if (isUnavailable(selectedId) && !updatedValue.includes(selectedId)) {
            mergedValue.splice(index, 0, selectedId);
        }
    });
    setSelectedValues(mergedValue);
}

function removeSelectedValue(removedId: string): void {
    setSelectedValues(
        selectedValues.value.filter((selectedId) => selectedId !== removedId),
    );
}

function buildResourceReference(selectedId: string): ResourceInstanceReference {
    const existingReference = aliasedNodeData?.node_value?.find(
        (resourceReference) => resourceReference.resourceId === selectedId,
    );
    if (existingReference) {
        return existingReference;
    }
    return {
        inverseRelationship: "",
        relationship: "",
        resourceId: selectedId,
        resourceXresourceId: "",
    };
}

function setSelectedValues(updatedValue: string[]): void {
    selectedValues.value = updatedValue;
    const nodeValues = updatedValue.map(buildResourceReference);
    const resolvedOptions = updatedValue
        .map((selectedId) =>
            options.value.find((option) => option.resource_id === selectedId),
        )
        .filter(
            (option): option is ResourceInstanceListOption =>
                option !== undefined,
        );
    emit(
        UPDATE_ALIASED_NODE_DATA_EVENT,
        buildResourceInstanceListAliasedNodeData(nodeValues, resolvedOptions),
    );
}

function onResourceCreated(createdTile: AliasedTileData): void {
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
        overlay-class="resource-instance-multiselect-widget-overlay"
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
            <div class="chip-label">
                <div class="chip-text">
                    {{ getChipLabel(slotProps.value) }}
                </div>
            </div>
            <div class="button-container">
                <template v-if="!isUnavailable(slotProps.value)">
                    <Button
                        class="no-text-decoration"
                        as="a"
                        icon="pi pi-info-circle"
                        target="_blank"
                        variant="text"
                        size="small"
                        :href="
                            generateArchesURL('arches:resource_report', {
                                resourceid: slotProps.value,
                            })
                        "
                        @click.stop
                    />
                    <Button
                        class="no-text-decoration"
                        as="a"
                        icon="pi pi-pencil"
                        target="_blank"
                        variant="text"
                        size="small"
                        :href="
                            generateArchesURL('arches:resource_editor', {
                                resourceid: slotProps.value,
                            })
                        "
                        @click.stop
                    />
                </template>
                <Button
                    icon="pi pi-times"
                    variant="text"
                    size="small"
                    @click.stop="removeSelectedValue(slotProps.value)"
                />
            </div>
        </template>
    </MultiSelect>

    <ResourceInstanceCreation
        v-if="showResourceCreation"
        :key="resourceCreationDialogKey"
        :graph-id="selectedGraphId"
        @resource-created="onResourceCreated"
    />
</template>

<style scoped>
.no-text-decoration {
    text-decoration: none;
}

.chip-label {
    inline-size: 100%;
}

.button-container {
    display: flex;
    justify-content: flex-end;
}

.chip-text {
    inline-size: min-content;
    min-inline-size: fit-content;
    overflow-wrap: anywhere;
    padding-block: 0.5rem;
    padding-inline: 1rem;
}

:deep(.p-multiselect-label) {
    inline-size: inherit;
    flex-direction: column;
    white-space: break-spaces;
    align-items: flex-start;
}

:deep(.p-multiselect-chip-item) {
    inline-size: inherit;
    border: 0.125rem solid
        var(--resource-instance-multiselect-chip-background, var(--p-blue-700));
    padding: 0.25rem;
    border-radius: 0.5rem;
    margin: 0.25rem;
    display: flex;
    background: var(
        --resource-instance-multiselect-chip-background,
        var(--p-blue-700)
    );
    color: var(--resource-instance-multiselect-chip-color, var(--p-surface-0));
}

:deep(.p-multiselect-chip-item .p-button),
:deep(.p-multiselect-chip-item .p-button:not(:disabled):hover) {
    border: none;
    color: var(
        --resource-instance-multiselect-chip-button-color,
        var(--p-surface-0)
    );
}

:deep(.p-multiselect-chip-item .p-button:not(:disabled):hover) {
    background: var(
        --resource-instance-multiselect-chip-button-hover-background,
        color-mix(
            in srgb,
            var(
                    --resource-instance-multiselect-chip-button-color,
                    var(--p-surface-0)
                )
                20%,
            transparent
        )
    );
}

:deep(.p-multiselect-label-container) {
    white-space: break-spaces;
    inline-size: inherit;
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
    padding-block: 0.5rem;
    padding-inline: 1rem;
    cursor: pointer;
}

.create-new-option:hover {
    background: var(--p-multiselect-option-focus-background);
}

.resource-instance-multiselect-widget-overlay .p-checkbox,
.resource-instance-multiselect-widget-overlay .p-checkbox-box {
    inline-size: 1.8rem;
    block-size: 1.8rem;
}

.resource-instance-multiselect-widget-overlay .p-checkbox-icon {
    inline-size: 1.2rem;
    block-size: 1.2rem;
    font-size: 1.2rem;
}
</style>
