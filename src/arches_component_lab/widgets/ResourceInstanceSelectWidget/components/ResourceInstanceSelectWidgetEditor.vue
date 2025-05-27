<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import { useGettext } from "vue3-gettext";
import { FormField } from "@primevue/forms";

import Message from "primevue/message";
import Select from "primevue/select";

import { fetchRelatableResources } from "@/arches_component_lab/widgets/api.ts";

import type { MultiSelectFilterEvent } from "primevue/multiselect";
import type { FormFieldResolverOptions } from "@primevue/forms";
import type { VirtualScrollerLazyEvent } from "primevue/virtualscroller";

import type {
    ResourceInstanceReference,
    ResourceInstanceResult,
} from "@/arches_component_lab/widgets/types.ts";

const props = defineProps<{
    initialValue: ResourceInstanceReference | null | undefined;
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

const resourceResultsCurrentCount = computed(() => options.value.length);

onMounted(async () => {
    await getOptions(1);
});

function clearOptions() {
    options.value = props.initialValue ? [props.initialValue] : [];
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
            props.initialValue ? [props.initialValue] : null,
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

function resolver(e: FormFieldResolverOptions) {
    validate(e);

    let value = e.value;

    return {
        values: {
            [props.nodeAlias]: options.value.find((option) => {
                return value && value === option.resourceId;
            }),
        },
    };
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
        v-slot="$field"
        :name="props.nodeAlias"
        :initial-value="props.initialValue?.resourceId"
        :resolver="resolver"
    >
        <Select
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
            }"
            @filter="onFilter"
            @before-show="getOptions(1)"
        >
        </Select>
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
