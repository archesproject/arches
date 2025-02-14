<script setup lang="ts">
import { computed, onMounted, ref, toRef, watch } from "vue";
import Button from "primevue/button";
import Dialog from "primevue/dialog";
import Message from "primevue/message";
import Select from "primevue/select";
import { useGettext } from "vue3-gettext";
import { fetchRelatableResources } from "@/arches_component_lab/widgets/api.ts";
import type { VirtualScrollerLazyEvent } from "primevue/virtualscroller";
import type { GraphInfo, NewResourceInstance, ResourceInstanceReference, ResourceInstanceResult } from "@/arches_component_lab/widgets/types.ts";

const showNewResource = ref(false);
const message = ref<MessageData | undefined>();
const { $gettext } = useGettext();
const props = defineProps<{
    initialValue?: ResourceInstanceReference[];
    configuration?: {
        graphSlug: string;
        nodeAlias: string;
        createNew?: boolean; // option to create a new resource; default false/undefined
        ptAriaLabeledBy?: string;
        itemHeight?: number;
        resultsPerPage?: number;
    }
}>();

const itemHeight = 38;
const resultsPerPage = 25;

interface MessageData {
    severity: 'successs' | 'info' | 'warn' | 'error';
    detail: string;
}

const rawValue = ref(props.initialValue?.[0]?.resourceId);

const isDirty = computed(() => rawValue.value !== props.initialValue);

const rawSelectedResources = computed({
    get() {
        return rawValue.value;
    },
    set(value) {
        rawValue.value = options.value.find(option => option.resourceId == value)?.resourceId
    }
}
);

defineExpose({
    rawValue,
    isDirty,
});


const options = ref<ResourceInstanceReference[]>([]);
const newElements = ref<NewResourceInstance[]>([]);
const isLoading = ref(false);
const isLoadingAdditionalResults = ref(false);
const computedResourceResultsHeight = ref("");
const resourceResultsPage = ref(1);
const resourceResultsTotalCount = ref(resultsPerPage);
watch(options, (resourceResults) => {
    if (resourceResults?.length) {
        const rootFontSize = parseFloat(
            getComputedStyle(document.documentElement).fontSize,
        );
        const itemHeightInRem = itemHeight / rootFontSize; // Convert to rem based on the root font size
        const computedHeightInRem = resourceResults.length * itemHeightInRem;

        const viewHeightInPixels = window.innerHeight * 0.6;
        const viewHeightInRem = viewHeightInPixels / rootFontSize; // Convert 60vh to rem

        if (computedHeightInRem > viewHeightInRem) {
            computedResourceResultsHeight.value = "60vh";
        } else {
            computedResourceResultsHeight.value = `${computedHeightInRem}rem`;
        }
    } else {
        computedResourceResultsHeight.value = "2.25rem";
    }
});

onMounted(() => {
    console.log('here i am')
    fetchData(1);
});

async function fetchData(page: number) {
    if (props.configuration) {
        try {
            const resourceData = await fetchRelatableResources(
                props.configuration.graphSlug,
                props.configuration.nodeAlias,
                page,
            );
            const references = resourceData.data.map(
                (
                    resourceRecord: ResourceInstanceResult,
                ): ResourceInstanceReference => ({
                    display_value: resourceRecord.display_value,
                    resourceId: resourceRecord.resourceinstanceid,
                    ontologyProperty: "",
                    inverseOntologyProperty: "",
                }),
            );

            if (page === 1) {
                options.value = references;
                newElements.value = resourceData.graphs.map(
                    (graphInfo: GraphInfo): NewResourceInstance => ({
                        displayValue: $gettext("Add a new %{graphName}", {
                            graphName: graphInfo.name,
                        }),
                        graphId: graphInfo.graphid,
                    }),
                );
            } else {
                options.value = [...options.value, ...references];
            }

            resourceResultsPage.value = resourceData.current_page;
            resourceResultsTotalCount.value = resourceData.total_results;
        } catch (error) {
            message.value = {
                detail: `Failed to fetch data.  ${error instanceof Error ? error.message : undefined}`,
                severity: "error",
            }

            options.value = [];
            resourceResultsPage.value = 1;
            resourceResultsTotalCount.value = 0;
        } finally {
            isLoading.value = false;
            isLoadingAdditionalResults.value = false;
        }
    }
}

async function onLazyLoadResources(event: VirtualScrollerLazyEvent) {
    if (
        event.last >= resourceResultsPage.value * resultsPerPage &&
        event.last <= resourceResultsTotalCount.value
    ) {
        isLoadingAdditionalResults.value = true;
        const page = resourceResultsPage.value + 1;
        fetchData(page);
    }
}

function createNewResource(graphId: string) {
    showNewResource.value = true;
    console.log(graphId);
}

function toggleSelectAll() {
    // check all selected then remove all selected items
    if (this.$refs.selectAll.allSelected) {
        this.selectedItems = [];
        return;
    }

    // else add all items
    this.selectAll = true;
}
</script>
<template>  
    <Select
        v-model="rawSelectedResources"
        :show-toggle-all="options?.length > 1"
        :options
        option-label="display_value"
        option-value="resourceId"
        class="resource-instance-relationships-selector"
        :virtual-scroller-options="{
            itemSize: itemHeight,
            lazy: true,
            onLazyLoad: onLazyLoadResources,
            scrollHeight: computedResourceResultsHeight,
            style: {
                minHeight: computedResourceResultsHeight,
                maxHeight: computedResourceResultsHeight,
            },
        }"
        :pt="{
            emptyMessage: { style: { fontFamily: 'sans-serif' } },
            option: { style: { fontFamily: 'sans-serif' } },
            overlay: { style: { fontFamily: 'sans-serif' } },
        }"
        :loading="isLoading && !isLoadingAdditionalResults"
        :placeholder="$gettext('Select Resources')"
    >
        <template #header>
            <div
                v-if="options.length > 1"
                class="select-all"
                @click="toggleSelectAll"
            >
                {{ $gettext("Select All Items") }}
            </div>
        </template>
        <template #footer>
            <div v-if="props?.configuration?.createNew">
                <div
                    v-for="element in newElements"
                    :key="`new-${element.graphId}`"
                >
                    <Button
                        class="relationship-footer-btn"
                        :label="element.displayValue"
                        severity="secondary"
                        variant="text"
                        @click="() => createNewResource(element.graphId)"
                    />
                </div>
            </div>
        </template>
    </Select>
    <Dialog
        v-model:visible="showNewResource"
        :header="$gettext('New Resource')"
        :dismissable-mask="true"
        :close-on-escape="true"
        :modal="true"
        :pt="{
            root: {
                style: {
                    borderRadius: '0',
                    fontFamily: 'sans-serif',
                },
            },
        }"
    ></Dialog>
    <Message v-if="message" :severity="message.severity">{{ message.detail }}</Message>
</template>
<style lang="css" scoped>
.relationship-footer-btn {
    width: 100%;
    border-radius: unset;
    justify-content: flex-start;
}

.select-all {
    position: absolute;
    top: 0.6rem;
    left: 2.7rem;
}
</style>