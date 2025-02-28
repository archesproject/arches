<script setup lang="ts">
import { computed, ref, useTemplateRef, watch } from "vue";

import arches from "arches";

import { useGettext } from "vue3-gettext";
import { FormField } from "@primevue/forms";

import Button from "primevue/button";
import Message from "primevue/message";
import MultiSelect from "primevue/multiselect";

import { fetchRelatableResources } from "@/arches_component_lab/widgets/api.ts";

import type { MultiSelectFilterEvent } from "primevue/multiselect";
import type { FormFieldResolverOptions } from "@primevue/forms";
import type { VirtualScrollerLazyEvent } from "primevue/virtualscroller";

import type {
    ResourceInstanceReference,
    ResourceInstanceResult,
} from "@/arches_component_lab/widgets/types.ts";

const props = defineProps<{
    initialValue: ResourceInstanceReference[] | undefined;
    graphSlug: string;
    nodeAlias: string;
}>();

const { $gettext } = useGettext();

const itemSize = 36; // in future iteration this should be declared in the CardXNodeXWidget config

const options = ref<ResourceInstanceReference[]>([]);
const isLoading = ref(false);
const resourceResultsPage = ref(0);
const resourceResultsTotalCount = ref(0);
const fetchError = ref<string | null>(null);

const formFieldRef = useTemplateRef("formFieldRef");

// this watcher is necessary to be able to format the value of the form field when the date picker is updated
watch(
    // @ts-expect-error - This is a bug in the PrimeVue types
    () => formFieldRef.value?.field?.states?.value,
    (newVal) => {
        if (!Array.isArray(newVal)) {
            newVal = [newVal];
        }

        if (
            newVal.length &&
            newVal.every((item: string | object) => typeof item === "string")
        ) {
            // @ts-expect-error - This is a bug in the PrimeVue types
            formFieldRef.value!.field.states.value = options.value.filter(
                (option) => {
                    return newVal?.includes(option.resourceId);
                },
            );
        }
    },
);

const resourceResultsCurrentCount = computed(() => options.value.length);

onMounted(async () => { await getOptions(1) });

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

        const resourceData = await fetchRelatableResources(
            props.graphSlug,
            props.nodeAlias,
            page,
            filterTerm,
            props.initialValue
        );
        console.log(resourceData);

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

        options.value = [...options.value, ...references];

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

// let timeout: ReturnType<typeof setTimeout>;

function resolver(e: FormFieldResolverOptions) {
    validate(e);
    // return new Promise((resolve) => {
    //     if (timeout) clearTimeout(timeout);

    //     timeout = setTimeout(() => {
    //         resolve(validate(e));
    //     }, 500);
    // });
}

function validate(e: FormFieldResolverOptions) {
    console.log("validate", e);
    // API call to validate the input
    // if (true) {
    //     return {};
    // } else {
    //     return {
    //         errors: [
    //             { message: "This is an error message" },
    //             { message: "This is also an error message" },
    //         ],
    //     };
    // }
}

function getOption(value: string): ResourceInstanceReference | undefined {
    const option = options.value.find((option) => option.resourceId == value);
    return option;
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
        :initial-value="props.initialValue?.map((resource) => resource.resourceId)
            "
        :resolver="resolver"
    >
        <MultiSelect
            class="resource-instance-multiselect-widget"
            display="chip"
            option-label="display_value"
            option-value="resourceId"
            :filter="true"
            :filter-placeholder="$gettext('Filter Resources')"
            :fluid="true"
            :loading="isLoading"
            :options
            :placeholder="$gettext('Select Resources')"
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
            <template
                #chip="//@ts-expect-error - This is a bug in the PrimeVue types
                    { value, removeCallback }"
            >
                <div class="p-multiselect-chip">
                    <span class="p-chip-label">
                        {{ getOption(value)?.display_value }}
                    </span>
                    <Button
                        icon="pi pi-pen-to-square"
                        :href="`${arches.urls.resource_editor}${value}`"
                        target="_blank"
                        variant="text"
                        as="a"
                        class="p-chip-button"
                        @click.stop="() => { }"
                    ></Button>
                    <Button
                        icon="pi pi-times-circle"
                        variant="text"
                        class="p-chip-button"
                        @click.stop="(e) => removeCallback(e, value)"
                    ></Button>
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
:deep(.resource-instance-multiselect-widget .p-multiselect-label) {
    visibility: visible;
    display: grid;
    min-width: 0;
    min-height: 0;
}

:deep(.resource-instance-multiselect-widget .p-multiselect-chip) {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto auto;
    align-items: center;
    min-width: 0;
    min-height: 0;
}

:deep(.resource-instance-multiselect-widget .p-multiselect-chip .pi) {
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
</style>

<!-- 
    This is a workaround for the checkboxes in the PrimeVue MultiSelect component 
    setting the FormField value to true/false instead of the selected options.
-->
<style>
.p-multiselect-overlay .p-checkbox {
    pointer-events: none;
}

.p-multiselect-overlay .p-multiselect-header .p-checkbox {
    pointer-events: all;
}
</style>
