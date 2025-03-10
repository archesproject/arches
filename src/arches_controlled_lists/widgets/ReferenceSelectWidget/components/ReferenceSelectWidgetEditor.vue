<script setup lang="ts">
import { ref, toRef, useTemplateRef } from "vue";

import { FormField } from "@primevue/forms";
import Message from "primevue/message";
import TreeSelect from "primevue/treeselect";

import { fetchWidgetOptions } from "@/arches_controlled_lists/widgets/api.ts";

import type { FormFieldResolverOptions } from "@primevue/forms";
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

const initialVal = toRef(
    props.configuration.multiValue
        ? props.initialValue?.map((reference) => extractInitialValue(reference))
        : extractInitialValue(
              props.initialValue ? props.initialValue[0] : undefined,
          ),
);

const options = ref<ReferenceSelectTreeNode[]>();
const isLoading = ref(false);
const optionsError = ref<string | null>(null);

function extractInitialValue(
    initialValue: ReferenceSelectFetchedOption | undefined,
) {
    if (!initialValue) {
        return {};
    }
    return { [initialValue?.list_item_id]: true };
}

function optionAsNode(
    item: ReferenceSelectFetchedOption | undefined,
): ReferenceSelectTreeNode {
    if (!item) {
        return {} as ReferenceSelectTreeNode;
    }
    return {
        key: item.list_item_id,
        label: item.display_value,
        sort_order: item.sort_order,
        children: item.children?.map((child) => optionAsNode(child)),
        data: item,
    };
}

function optionsAsNodes(
    items: ReferenceSelectFetchedOption[],
): ReferenceSelectTreeNode[] {
    return items.map((item) => optionAsNode(item));
}

async function getOptions() {
    isLoading.value = true;
    try {
        const fetchedLists = await fetchWidgetOptions(
            props.graphSlug,
            props.nodeAlias,
        );
        options.value = optionsAsNodes(fetchedLists);
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
