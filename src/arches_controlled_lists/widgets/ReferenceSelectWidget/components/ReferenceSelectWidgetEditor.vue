<script setup lang="ts">
import { ref, useTemplateRef, watch } from "vue";

import { FormField } from "@primevue/forms";
import Message from "primevue/message";
import TreeSelect from "primevue/treeselect";

import { fetchWidgetOptions } from "@/arches_controlled_lists/widgets/api.ts";

import type { FormFieldResolverOptions } from "@primevue/forms";
import type {
    ControlledListItemTileValue,
    ReferenceSelectTreeNode,
    ReferenceSelectFetchedOption,
} from "@/arches_controlled_lists/widgets/types";

const props = defineProps<{
    initialValue: ControlledListItemTileValue[] | undefined;
    configuration: {
        placeholder: string;
    };
    nodeAlias: string;
    graphSlug: string;
}>();

const options = ref<ReferenceSelectTreeNode[]>();
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
                options.value?.find(
                    (option: ReferenceSelectTreeNode) => option.uri === newVal,
                ),
            ];
        }
    },
);

function optionAsNode(
    item: ReferenceSelectFetchedOption,
): ReferenceSelectTreeNode {
    return {
        key: item.list_item_id,
        label: item.display_label,
        sort_order: item.sort_order,
        children: item.children.map((child) => optionAsNode(child)),
        data: item,
    };
}

async function getOptions() {
    isLoading.value = true;
    try {
        const fetchedLists = await fetchWidgetOptions(
            props.graphSlug,
            props.nodeAlias,
        );
        options.value = fetchedLists.map((item: ReferenceSelectFetchedOption) =>
            optionAsNode(item),
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
        <TreeSelect
            style="display: flex"
            option-value="uri"
            :fluid="true"
            :loading="isLoading"
            :options="options"
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
