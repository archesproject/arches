<script setup lang="ts">
import { useTemplateRef, watch } from "vue";
import dayjs from "dayjs";

import DatePicker from "primevue/datepicker";
import Message from "primevue/message";

import { FormField } from "@primevue/forms";
import type { FormFieldResolverOptions } from "@primevue/forms";

const props = defineProps<{
    initialValue: string | undefined;
    graphSlug: string;
    nodeAlias: string;
    widgetData: {
        config: {
            dateFormat: string;
            datePickerDisplayConfiguration: {
                dateFormat: string;
                shouldShowTime: boolean;
            }
        }
    };
}>();

const formFieldRef = useTemplateRef("formFieldRef");

// this watcher is necessary to be able to format the value of the form field when the date picker is updated
watch(
    // @ts-expect-error - This is a bug in the PrimeVue types
    () => formFieldRef.value?.field?.states?.value,
    (newVal, oldVal) => {
        if (newVal !== oldVal) {
            // @ts-expect-error - This is a bug in the PrimeVue types
            formFieldRef.value!.field.states.value = dayjs(newVal).format(
                props.widgetData.config.dateFormat,
            );
        }
    },
);

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
    <FormField
        ref="formFieldRef"
        v-slot="$field"
        :name="props.nodeAlias"
        :initial-value="props.initialValue"
        :resolver="resolver"
    >
        <DatePicker
            icon-display="input"
            :date-format="
                props.widgetData.config.datePickerDisplayConfiguration.dateFormat
            "
            :fluid="true"
            :show-icon="true"
            :show-time="
                props.widgetData.config.datePickerDisplayConfiguration
                    .shouldShowTime
            "
            :show-seconds="
                props.widgetData.config.datePickerDisplayConfiguration
                    .shouldShowTime
            "
            @keydown.enter.prevent
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
