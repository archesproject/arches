<script setup lang="ts">
import { ref, useTemplateRef, watch } from "vue";

import { FormField } from "@primevue/forms";
import Message from "primevue/message";
import Select from "primevue/select";

import { fetchWidgetOptions } from "@/arches_controlled_lists/widgets/api.ts";

import type { FormFieldResolverOptions } from "@primevue/forms";
import type { ReferenceOptionValue } from "@/arches_controlled_lists/widgets/types";

const props = defineProps<{
    initialValue: ReferenceOptionValue[] | undefined;
    configuration: {
        placeholder: string;
    };
    nodeAlias: string;
    graphSlug: string;
}>();

const options = ref<ReferenceOptionValue[]>(props.initialValue || []);
const isLoading = ref(false);
const optionsError = ref<string | null>(null);

const formFieldRef = useTemplateRef("formFieldRef");

// this watcher is necessary to be able to format the value of the form field when the dropdown is updated
watch(
    // @ts-expect-error - This is a bug in the PrimeVue types
    () => formFieldRef.value?.field?.states?.value,
    (newVal) => {
        if (typeof newVal === "string") {
            // @ts-expect-error - This is a bug in the PrimeVue types
            formFieldRef.value!.field.states.value = [
                options.value.find(
                    (option: ReferenceOptionValue) => option.uri === newVal,
                ),
            ];
        }
    },
);

async function getOptions() {
    isLoading.value = true;
    try {
        const fetchedLists = await fetchWidgetOptions(
            props.graphSlug,
            props.nodeAlias,
        );
        options.value = fetchedLists;
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
            :option-label="displayValue"
            :placeholder="configuration.placeholder"
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
