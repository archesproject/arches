<script setup lang="ts">
import InputText from "primevue/inputtext";
import Message from "primevue/message";

import { FormField, type FormFieldResolverOptions } from "@primevue/forms";

const props = defineProps<{
    nodeAlias: string;
    graphSlug: string;
    value: string | null | undefined;
}>();

const emit = defineEmits(["update:value"]);

function resolver(event: FormFieldResolverOptions) {
    validate(event);

    emit("update:value", event.value);

    return {
        values: { [props.nodeAlias]: event.value },
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
        :initial-value="props.value"
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
