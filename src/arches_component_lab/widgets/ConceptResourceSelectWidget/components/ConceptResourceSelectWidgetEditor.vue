<script setup lang="ts">
import arches from "arches";
import { computed, ref, useTemplateRef } from "vue";

import { useGettext } from "vue3-gettext";
import { FormField } from "@primevue/forms";

import Message from "primevue/message";
import MultiSelect from "primevue/multiselect";

import { fetchConceptResources } from "@/arches_lingo/api.ts";
import { getItemLabel } from "@/arches_vue_utils/utils.ts";
import { getParentLabels } from "@/arches_lingo/utils.ts";
import { ENGLISH } from "@/arches_lingo/constants.ts";

import type { MultiSelectFilterEvent } from "primevue/multiselect";
import type { FormFieldResolverOptions } from "@primevue/forms";
import type { VirtualScrollerLazyEvent } from "primevue/virtualscroller";

import type { SearchResultItem } from "@/arches_lingo/types.ts";

const props = defineProps<{
    initialValue: SearchResultItem[] | null | undefined;
    graphSlug: string;
    nodeAlias: string;
    scheme: string;
    exclude: boolean;
}>();

props.initialValue?.forEach((option) => {
    option.label = getItemLabel(option, ENGLISH.code, ENGLISH.code).value;
});

const { $gettext } = useGettext();

const itemSize = 36; // in future iteration this should be declared in the CardXNodeXWidget config

const options = ref<SearchResultItem[]>(props.initialValue || []);
const isLoading = ref(false);
const searchResultsPage = ref(0);
const searchResultsTotalCount = ref(0);
const fetchError = ref<string | null>(null);


const searchResultsCurrentCount = computed(() => options.value.length);

function clearOptions() {
    options.value = props.initialValue || [];
}

function onFilter(event: MultiSelectFilterEvent) {
    clearOptions();
    getOptions(1, event.value);
}

async function getOptions(page: number, filterTerm?: string) {
    try {
        isLoading.value = true;
        const parsedResponse = await fetchConceptResources(
            filterTerm || "",
            itemSize,
            page,
            props.scheme,
            props.exclude,
        );

        parsedResponse.data.forEach((option: SearchResultItem) => {
            option.label = getItemLabel(
                option,
                ENGLISH.code,
                ENGLISH.code,
            ).value;
        });
        if (page === 1) {
            options.value = parsedResponse.data;
        } else {
            options.value = [...options.value, ...parsedResponse.data];
        }

        searchResultsPage.value = parsedResponse.current_page;
        searchResultsTotalCount.value = parsedResponse.total_results;
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
        searchResultsTotalCount.value > 0 &&
        searchResultsCurrentCount.value >= searchResultsTotalCount.value
    ) {
        return;
    }

    if (
        // if the user has NOT scrolled to the end of the list
        event &&
        event.last < searchResultsCurrentCount.value - 1
    ) {
        return;
    }

    if (
        // if the dropdown is opened and we already have data
        !event &&
        searchResultsCurrentCount.value > 0
    ) {
        return;
    }

    await getOptions((searchResultsPage.value || 0) + 1);
}

function resolver(e: FormFieldResolverOptions) {
    validate(e);
}

function validate(e: FormFieldResolverOptions) {
    console.log("validate", e);
}
</script>

<template>
    <Message
        v-if="fetchError"
        severity="error"
    >
        {{ fetchError }}
    </Message>
    <FormField
        v-else
        ref="formFieldRef"
        v-slot="$field"
        :name="props.nodeAlias"
        :initial-value="props.initialValue?.map((concept) => concept.id)"
        :resolver="resolver"
    >
        <MultiSelect
            class="concept-resource-select-widget"
            display="chip"
            option-label="label"
            option-value="id"
            :filter="true"
            :filter-placeholder="$gettext('Filter Concepts')"
            :fluid="true"
            :loading="isLoading"
            :options
            :placeholder="$gettext('Select Concepts')"
            :reset-filter-on-hide="true"
            :virtual-scroller-options="{
                itemSize: itemSize,
                lazy: true,
                loading: isLoading,
                onLazyLoad: onLazyLoadResources,
                resizeDelay: 200,
            }"
            @before-show="getOptions(1)"
            @filter="onFilter"
        >
            <template #option="slotProps">
                <div class="flex items-center">
                    <span>
                        {{
                            getItemLabel(
                                slotProps.option,
                                ENGLISH.code,
                                ENGLISH.code,
                            ).value
                        }}
                    </span>
                    <span class="concept-hierarchy">
                        [
                        {{
                            getParentLabels(
                                slotProps.option,
                                ENGLISH.code,
                                ENGLISH.code,
                            )
                        }}
                        ]
                    </span>
                    <Button
                        icon="pi pi-pen-to-square"
                        :href="`${arches.urls.resource_editor}${slotProps.option.id}`"
                        target="_blank"
                        variant="text"
                        as="a"
                        class="p-chip-button"
                    />
                    <Button
                        icon="pi pi-times-circle"
                        variant="text"
                        class="p-chip-button"
                        @click.stop="
                            (e) =>
                                (slotProps as any).removeCallback(
                                    e,
                                    slotProps.option,
                                )
                        "
                    />
                </div>
            </template>
        </MultiSelect>
        <Message
            v-for="error in $field.errors"
            :key="error.message"
            severity="error"
            size="small"
        >
            {{ error.message }}
        </Message>
    </FormField>
</template>
<style scoped>
:deep(.concept-resource-select-widget .p-multiselect-label) {
    visibility: visible;
    display: grid;
    min-width: 0;
    min-height: 0;
}

:deep(.concept-resource-select-widget .p-multiselect-chip) {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto auto;
    align-items: center;
    min-width: 0;
    min-height: 0;
}

:deep(.concept-resource-select-widget .p-multiselect-chip .pi) {
    margin: 0 0.5rem;
}

:deep(.p-chip) {
    overflow: hidden;
    min-width: 0;
    min-height: 0;
}

:deep(.p-multiselect-chip .p-chip-button) {
    text-decoration: none;
}

:deep(.p-multiselect-option span) {
    overflow: hidden;
    text-overflow: ellipsis;
}

:deep(.p-chip-label) {
    overflow: hidden;
    word-wrap: nowrap;
    text-overflow: ellipsis;
    min-width: 0;
    max-width: 100%;
}
.concept-hierarchy {
    font-size: small;
    color: steelblue;
}
</style>
