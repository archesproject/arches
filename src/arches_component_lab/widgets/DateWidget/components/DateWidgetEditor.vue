<script setup lang="ts">
import DatePicker from "primevue/datepicker";
import Message from "primevue/message";

import { FormField } from "@primevue/forms";
import type { FormFieldResolverOptions } from "@primevue/forms";

const props = defineProps<{
    initialValue: Date | undefined;
    configuration: {
        dateFormat: string;
        graphSlug: string;
        label: string;
        nodeAlias: string;
    };
}>();

let timeout: ReturnType<typeof setTimeout>;

function resolver(e: FormFieldResolverOptions) {
    return new Promise((resolve) => {
        if (timeout) clearTimeout(timeout);

        timeout = setTimeout(() => {
            resolve(validate(e));
        }, 500);
    });
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
function validate(e: FormFieldResolverOptions) {
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
    <!-- TODO: HANDLE TIMEZONE/DATE FORMATTING -->
    <FormField
        v-slot="$field"
        :name="props.configuration.nodeAlias"
        :initial-value="props.initialValue"
        :resolver="resolver"
    >
        <DatePicker
            icon-display="input"
            :date-format="configuration.dateFormat"
            :show-icon="true"
            :fluid="true"
            :manual-input="true"
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
