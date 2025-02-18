<script setup lang="ts">
import { computed, ref, useTemplateRef, watch } from "vue";

import { useGettext } from "vue3-gettext";

import { FormField } from "@primevue/forms";
import Message from "primevue/message";
// import Select from "primevue/select";
import MultiSelect from "primevue/multiselect";

import { fetchRelatableResources } from "@/arches_component_lab/widgets/api.ts";

import type { FormFieldResolverOptions } from "@primevue/forms";
import type { VirtualScrollerLazyEvent } from "primevue/virtualscroller";
import type {
    ResourceInstanceReference,
    ResourceInstanceResult,
} from "@/arches_component_lab/widgets/types.ts";

const props = defineProps<{
    initialValue: ResourceInstanceReference[];
    graphSlug: string;
    nodeAlias: string;
}>();

const { $gettext } = useGettext();

const itemSize = 36; // in future iteration this should be declared in the CardXNodeXWidget config

const options = ref<ResourceInstanceReference[]>(props.initialValue);
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
        if (
            newVal.length &&
            newVal.every((item: string | object) => typeof item === "string")
        ) {
            // @ts-expect-error - This is a bug in the PrimeVue types
            formFieldRef.value!.field.states.value = options.value.filter(
                (option) => newVal?.includes(option.resourceId),
            );
        }
    },
);

const resourceResultsCurrentCount = computed(() => options.value.length);

async function fetchData(page: number) {
    try {
        isLoading.value = true;

        const resourceData = await fetchRelatableResources(
            props.graphSlug,
            props.nodeAlias,
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
    if (isLoading.value) { return; }

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

    await fetchData((resourceResultsPage.value || 0) + 1);
}

let timeout: ReturnType<typeof setTimeout>;

function resolver(e: FormFieldResolverOptions) {
    return new Promise((resolve) => {
        if (timeout) clearTimeout(timeout);

        timeout = setTimeout(() => {
            resolve(validate(e));
        }, 500);
    });
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
        :initial-value="
            props.initialValue.map((resource) => resource.resourceId)
        "
        :resolver="resolver"
    >
        <MultiSelect
            class="resource-instance-multiselect-widget"
            display="chip"
            option-label="display_value"
            option-value="resourceId"
            :fluid="true"
            :loading="isLoading"
            :options
            :placeholder="$gettext('Select Resources')"
            :virtual-scroller-options="{
                itemSize: itemSize,
                lazy: true,
                loading: isLoading,
                onLazyLoad: onLazyLoadResources,
            }"
            @before-show="onLazyLoadResources"
        />
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
<style>
.resource-instance-multiselect-widget .p-multiselect-label {
    visibility: visible !important;
    display: grid !important;
}

.resource-instance-multiselect-widget .p-multiselect-chip {
    display: grid !important;
    grid-template-columns: 1fr auto;
}

.resource-instance-multiselect-widget .p-chip-label {
    max-width: min-content;
    white-space: normal;
}
</style>
