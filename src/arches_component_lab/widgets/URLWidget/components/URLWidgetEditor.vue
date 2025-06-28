<script setup lang="ts">
import { useTemplateRef } from "vue";

import InputText from "primevue/inputtext";
import Message from "primevue/message";

import { FormField, type FormFieldResolverOptions } from "@primevue/forms";

import type { URLDatatype } from "@/arches_component_lab/widgets/types.ts";

const props = defineProps<{
    nodeAlias: string;
    graphSlug: string;
    value: URLDatatype | null | undefined;
}>();

const emit = defineEmits(["update:isDirty", "update:value"]);

const formFieldRef = useTemplateRef("formField");

function resolver(event: FormFieldResolverOptions) {
    validate(event);

    // @ts-expect-error This is a bug with PrimeVue types
    emit("update:isDirty", Boolean(formFieldRef.value!.fieldAttrs.dirty));
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
        ref="formField"
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
