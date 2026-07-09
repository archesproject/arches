<script setup lang="ts">
import { computed, ref, watch, watchEffect } from "vue";

import { useGettext } from "vue3-gettext";

import Select from "primevue/select";

import ResourceInstanceCreation from "@/arches_component_lab/widgets/components/ResourceInstanceCreation.vue";

import { fetchRelatableResources } from "@/arches_component_lab/datatypes/resource-instance/api.ts";
import { buildResourceInstanceAliasedNodeData } from "@/arches_component_lab/datatypes/resource-instance/utils.ts";
import { debounce } from "@/arches_component_lab/utils.ts";

import type { SelectFilterEvent } from "primevue/select";
import type { VirtualScrollerLazyEvent } from "primevue/virtualscroller";

import type {
    ResourceInstanceReference,
    ResourceInstanceDataItem,
    ResourceInstanceSelectOption,
    ResourceInstanceCardXNodeXWidgetData,
} from "@/arches_component_lab/datatypes/resource-instance/types.ts";

import type { AliasedTileData } from "@/arches_component_lab/types";
import type { ResourceInstanceAliasedNodeData } from "@/arches_component_lab/datatypes/resource-instance/types.ts";

// in future iteration these may be declared in the CardXNodeXWidgetData config
const ITEM_SIZE = 36;

const {
    cardXNodeXWidgetData,
    nodeAlias,
    graphSlug,
    aliasedNodeData,
    defaultTerm,
} = defineProps<{
    cardXNodeXWidgetData?: ResourceInstanceCardXNodeXWidgetData;
    nodeAlias?: string;
    graphSlug?: string;
    aliasedNodeData?: ResourceInstanceAliasedNodeData | null;
    defaultTerm?: string;
}>();

const emit = defineEmits<{
    (event: "update:isLoading", isLoading: boolean): void;
    (
        event: "update:aliasedNodeData",
        updatedValue: ResourceInstanceAliasedNodeData,
    ): void;
    (event: "initialized", updatedValue: ResourceInstanceAliasedNodeData): void;
}>();

const { $gettext } = useGettext();

const options = ref<ResourceInstanceSelectOption[]>([]);
const isLoading = ref(false);
const resourceResultsPage = ref(0);
const resourceResultsTotalCount = ref(0);
const fetchError = ref<string | null>(null);
const emptyFilterMessage = ref($gettext("Search returned no results"));

const selectedGraphId = ref<string>("");
const showResourceCreation = ref(false);
const resourceCreationDialogKey = ref(0);

const selectedValue = ref<string | null>(
    aliasedNodeData?.node_value?.[0]?.resourceId ?? null,
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
            selectedValue.value,
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
        if (options.value.length === 0) {
            emptyFilterMessage.value = $gettext("Search returned no results");
        }
        if (page === 1 && !hasInitialized.value) {
            hasInitialized.value = true;
            const displayName =
                options.value.find(
                    (option) => option.resource_id === selectedValue.value,
                )?.display_value ?? "";
            emit(
                "initialized",
                aliasedNodeData ??
                    buildResourceInstanceAliasedNodeData(null, displayName),
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

const onFilter = debounce(function onFilterDebounced(event: SelectFilterEvent) {
    getOptions(1, event.value);
}, 600);

function onCreateNewResource(graphId: string) {
    selectedGraphId.value = graphId;
    resourceCreationDialogKey.value++;
    showResourceCreation.value = true;
}

function onUpdateModelValue(updatedValue: string | null) {
    selectedValue.value = updatedValue;
    if (updatedValue) {
        const nodeValue: ResourceInstanceReference = {
            inverseOntologyProperty: "",
            ontologyProperty: "",
            resourceId: updatedValue,
            resourceXresourceId: "",
        };
        const displayName =
            options.value.find((option) => option.resource_id === updatedValue)
                ?.display_value ?? "";
        emit(
            "update:aliasedNodeData",
            buildResourceInstanceAliasedNodeData(nodeValue, displayName),
        );
    } else {
        emit(
            "update:aliasedNodeData",
            buildResourceInstanceAliasedNodeData(null, ""),
        );
    }
}

async function onResourceCreated(createdTile: AliasedTileData) {
    selectedValue.value = createdTile.resourceinstance;
    getOptions(1);
    onUpdateModelValue(selectedValue.value);
    showResourceCreation.value = false;
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
        :input-id="cardXNodeXWidgetData?.node.alias"
        :label-id="cardXNodeXWidgetData?.node.alias"
        :loading="isLoading"
        :model-value="selectedValue"
        :options="options"
        :placeholder="cardXNodeXWidgetData?.config.placeholder"
        :reset-filter-on-hide="true"
        :show-clear="true"
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
    </Select>
    <ResourceInstanceCreation
        v-if="showResourceCreation"
        :key="resourceCreationDialogKey"
        :graph-id="selectedGraphId!"
        @resource-created="onResourceCreated"
    />
</template>

<style>
.p-select-overlay {
    display: flex;
    flex-direction: column;
}

.p-select-header {
    order: 0;
}

.create-new-options-header {
    order: 1;
}

.p-select-list-container,
.p-virtualscroller {
    order: 2;
}

.create-new-option {
    font-weight: bold;
    padding: 0.5rem 1rem;
    cursor: pointer;
}

.create-new-option:hover {
    background: var(--p-select-option-focus-background);
}
</style>
