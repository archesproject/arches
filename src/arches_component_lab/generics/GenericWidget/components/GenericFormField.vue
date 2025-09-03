<script setup lang="ts">
import { useTemplateRef, watchEffect } from "vue";

import { FormField, type FormFieldResolverOptions } from "@primevue/forms";
import Message from "primevue/message";

import type { AliasedNodeData } from "@/arches_component_lab/types.ts";

type FormFieldType = {
    field: {
        states: {
            dirty: boolean;
            pristine: boolean;
            touched: boolean;
        };
        errors: Array<{ message: string }>;
        props: {
            onChange: (event: { value: AliasedNodeData }) => void;
        };
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

const formFieldRef = useTemplateRef<FormFieldType>("formField");

// cannot inline, this allows the dirty state to be set on first input
const initialValue = Object.freeze({ ...aliasedNodeData });

watchEffect(() => {
    if (isDirty) {
        markFormFieldAsDirty();
    }
});

function markFormFieldAsDirty() {
    if (!formFieldRef.value) {
        return;
    }

    formFieldRef.value.field.states.dirty = true;
    formFieldRef.value.field.states.pristine = false;
    formFieldRef.value.field.states.touched = true;
}

function resolver(
    updatedAliasedNodeData: FormFieldResolverOptions,
): AliasedNodeData {
    validate(updatedAliasedNodeData as unknown as AliasedNodeData);
    return updatedAliasedNodeData as unknown as AliasedNodeData;
}

function validate(aliasedNodeData: AliasedNodeData) {
    console.log("validateValue", aliasedNodeData);
}

function onUpdateValue(updatedAliasedNodeData: AliasedNodeData) {
    if (aliasedNodeData === updatedAliasedNodeData) {
        return;
    }

    formFieldRef.value?.field.props.onChange({ value: updatedAliasedNodeData });

    emit("update:value", updatedAliasedNodeData);
    emit("update:isDirty", true);
}
</script>

<template>
    <slot :on-update-value="onUpdateValue" />

    <FormField
        ref="formField"
        v-slot="$field"
        :name="nodeAlias"
        :resolver="resolver"
        :initial-value="initialValue"
    >
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
