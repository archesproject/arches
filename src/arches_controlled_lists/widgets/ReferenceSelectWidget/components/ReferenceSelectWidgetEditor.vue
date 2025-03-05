<script setup lang="ts">
import { ref, useTemplateRef, watch } from "vue";

import { FormField } from "@primevue/forms";
import Message from "primevue/message";
import Select from "primevue/select";

import { fetchLists } from "@/arches_component_lab/widgets/api.ts";

import type { FormFieldResolverOptions } from "@primevue/forms";
import type { ControlledListItem } from "@/arches_controlled_lists/types";

const props = defineProps<{
    initialValue: ControlledListItem[] | undefined;
    widgetData: {
        config: {
            palceholder: string
        }
    };
    nodeAlias: string;
    graphSlug: string;
}>();

const options = ref<ControlledListItem[]>(props.initialValue || []);
const isLoading = ref(false);
const optionsError = ref<string | null>(null);

const formFieldRef = useTemplateRef("formFieldRef");

// this watcher is necessary to be able to format the value of the form field when the date picker is updated
watch(
    // @ts-expect-error - This is a bug in the PrimeVue types
    () => formFieldRef.value?.field?.states?.value,
    (newVal) => {
        if (typeof newVal === "string") {
            // @ts-expect-error - This is a bug in the PrimeVue types
            formFieldRef.value!.field.states.value = [
                options.value.find(
                    (option: ControlledListItem) => option.uri === newVal,
                ),
            ];
        }
    },
);

async function getOptions() {
    isLoading.value = true;

    try {
        const fetchedLists = await fetchLists([props.nodeAlias]);

        options.value = fetchedLists.controlled_lists[0].items.map(
            (item: ControlledListItem) => ({
                list_id: item.list_id,
                uri: item.uri,
                labels: item.values,
            }),
        );
    } catch (error) {
        optionsError.value = (error as Error).message;
    } finally {
        isLoading.value = false;
    }
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

// THIS SHOULD NOT EXIST, THE API SHOULD RETURN A MORE SIMPLIFIED RESPONSE
function getOptionLabels(item: {
    labels: [{ valuetype_id: string; language_id: string; value: string }];
}): string {
    const prefLabels = item.labels.filter(
        (label) => label.valuetype_id === "prefLabel",
    );
    const optionLabel =
        prefLabels.find((label) => label.language_id === "en") || prefLabels[0];
    return optionLabel?.value ?? "";
}
</script>

<template>
    <Message
        v-if="optionsError"
        severity="error"
    >
        {{ optionsError }}
    </Message>
    <FormField
        v-else
        ref="formFieldRef"
        v-slot="$field"
        :name="props.nodeAlias"
        :resolver="resolver"
        :initial-value="props.initialValue && props.initialValue[0].uri"
    >
        <Select
            style="display: flex"
            option-value="uri"
            :fluid="true"
            :loading="isLoading"
            :options="options"
            :option-label="getOptionLabels"
            :placeholder="widgetData.config.placeholder"
            :show-clear="true"
            @before-show="getOptions"
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
