<script setup lang="ts">
import { useTemplateRef, watchEffect, watch } from "vue";

import { FormField } from "@primevue/forms";
import Message from "primevue/message";

import type { AliasedNodeData } from "@/arches_component_lab/types.ts";

type FieldStates = {
    dirty: boolean;
    pristine: boolean;
    touched: boolean;
};

type FormFieldExposed = {
    field: {
        states: FieldStates;
        errors: Array<{ message: string }>;
    };
};

const { isDirty, nodeAlias, aliasedNodeData } = defineProps<{
    isDirty: boolean;
    nodeAlias: string;
    aliasedNodeData: AliasedNodeData;
}>();

const emit = defineEmits<{
    (e: "update:value", newValue: AliasedNodeData): void;
    (e: "update:isDirty", dirty: boolean): void;
}>();

const formFieldRef = useTemplateRef<FormFieldExposed>("formField");

// cannot inline, this allows the dirty state to be set on first input
const initialValue = Object.freeze({ ...aliasedNodeData });

watchEffect(() => {
    if (isDirty) {
        markFormFieldAsDirty();
    }
});

watch(
    () => aliasedNodeData,
    (newValue, oldValue) => {
        if (newValue !== oldValue) {
            emit("update:value", newValue);
            emit("update:isDirty", true);
        }
    },
    { deep: true },
);

function markFormFieldAsDirty() {
    if (!formFieldRef.value) {
        return;
    }

    formFieldRef.value.field.states.dirty = true;
    formFieldRef.value.field.states.pristine = false;
    formFieldRef.value.field.states.touched = true;
}

function resolver() {
    validate(aliasedNodeData);
    return aliasedNodeData;
}

function validate(aliasedNodeData: AliasedNodeData) {
    console.log("validateValue", aliasedNodeData);
}
</script>

<template>
    <FormField
        ref="formField"
        v-slot="$field"
        :name="nodeAlias"
        :resolver="resolver"
        :initial-value="initialValue"
    >
        <slot v-bind="$field" />

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
