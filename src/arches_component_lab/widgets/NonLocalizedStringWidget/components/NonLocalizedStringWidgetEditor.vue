<script setup lang="ts">
import InputText from "primevue/inputtext";
import Message from "primevue/message";

import { FormField, type FormFieldResolverOptions } from "@primevue/forms";

const props = defineProps<{
    initialValue: string | null | undefined;
    nodeAlias: string;
    graphSlug: string;
}>();

function resolver(e: FormFieldResolverOptions) {
    validate(e);

    return {
        values: { [props.nodeAlias]: e.value },
    };
}

function validate(e: FormFieldResolverOptions) {
    console.log("validate", e);
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
            :id="`${props.graphSlug}-${props.nodeAlias}-input`"
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
