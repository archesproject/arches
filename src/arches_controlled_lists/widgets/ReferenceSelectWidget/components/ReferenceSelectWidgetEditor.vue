<script setup lang="ts">
import { ref, toRef, useTemplateRef, watch } from "vue";

import { FormField } from "@primevue/forms";
import Message from "primevue/message";
import TreeSelect from "primevue/treeselect";

import { fetchWidgetOptions } from "@/arches_controlled_lists/widgets/api.ts";

import type { Ref } from "vue";
import type { FormFieldResolverOptions } from "@primevue/forms";
import type { TreeExpandedKeys } from "primevue/tree";
import type {
    ReferenceSelectTreeNode,
    ReferenceSelectFetchedOption,
} from "@/arches_controlled_lists/widgets/types";

const props = defineProps<{
    initialValue: ReferenceSelectFetchedOption[] | undefined;
    configuration: {
        placeholder: string;
        controlledList: string;
        multiValue: boolean;
    };
    nodeAlias: string;
    graphSlug: string;
}>();

const formFieldRef = useTemplateRef("formFieldRef");

// this watcher is necessary to be able to format the value of the form field when the dropdown is updated
watch(
    // @ts-expect-error - This is a bug in the PrimeVue types
    () => formFieldRef.value?.field?.states?.value,
    (newVal) => {
        // PrimeVue's v-model for TreeSelect is an obj with the selected items as keys with True as value:
        // {"list_item_id_1": true, "list_item_id_2": true}
        if (newVal && typeof newVal === "object") {
            const selectedItemKeys = Object.entries(newVal).reduce<string[]>(
                (keys, [key, value]) => {
                    if (value === true) keys.push(key);
                    return keys;
                },
                [],
            );

            if (selectedItemKeys.length && !("key" in selectedItemKeys)) {
                // @ts-expect-error - This is a bug in the PrimeVue types
                formFieldRef.value!.field.states.value = selectedItemKeys;
            }
        } else {
            // @ts-expect-error - This is a bug in the PrimeVue types
            formFieldRef.value!.field.states.value = [];
        }
    },
);

const options = ref<ReferenceSelectTreeNode[]>();
const isLoading = ref(false);
const optionsError = ref<string | null>(null);
const expandedKeys: Ref<TreeExpandedKeys> = ref({});

const initialVal = toRef(
    props.configuration.multiValue
        ? props.initialValue?.map((reference) => extractInitialValue(reference))
        : extractInitialValue(
              props.initialValue ? props.initialValue[0] : undefined,
          ),
);

function extractInitialValue(
    initialValue: ReferenceSelectFetchedOption | undefined,
) {
    if (!initialValue) {
        return undefined;
    }
    return { [initialValue?.list_item_id]: true };
}

function optionAsNode(
    item: ReferenceSelectFetchedOption,
): ReferenceSelectTreeNode {
    expandedKeys.value = {
        ...expandedKeys.value,
        [item.list_item_id]: true,
    };
    return {
        key: item.list_item_id,
        label: item.display_value,
        children: item.children?.map(optionAsNode),
        data: item,
    };
}

function optionsAsNodes(
    items: ReferenceSelectFetchedOption[],
): ReferenceSelectTreeNode[] {
    return items
        .filter((item): item is ReferenceSelectFetchedOption => !!item)
        .map(optionAsNode);
}

async function getOptions() {
    isLoading.value = true;
    try {
        const fetchedLists = await fetchWidgetOptions(
            props.graphSlug,
            props.nodeAlias,
        );
        options.value = fetchedLists ? optionsAsNodes(fetchedLists) : [];
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
        :initial-value="initialVal"
    >
        <TreeSelect
            style="display: flex"
            option-value="list_item_id"
            :fluid="true"
            :loading="isLoading"
            :options="options"
            :expanded-keys="expandedKeys"
            :placeholder="configuration.placeholder"
            :selection-mode="configuration.multiValue ? 'multiple' : 'single'"
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
