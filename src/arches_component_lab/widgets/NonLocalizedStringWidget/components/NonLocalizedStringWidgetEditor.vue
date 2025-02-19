<script setup lang="ts">
import InputText from "primevue/inputtext";
import Message from "primevue/message";

import { FormField, type FormFieldResolverOptions } from "@primevue/forms";

const props = defineProps<{
    initialValue: string | undefined;
    nodeAlias: string;
    graphSlug: string;
    configuration: any;
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
    <FormField
        v-slot="$field"
        :name="props.nodeAlias"
        :initial-value="props.initialValue"
        :resolver="resolver"
    >
        <InputText
            type="text"
            :fluid="true"
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
