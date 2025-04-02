<script setup lang="ts">
import { onMounted, ref, toRef, useTemplateRef, watch } from "vue";

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
        defaultValue: ReferenceSelectFetchedOption[] | undefined;
    };
    nodeAlias: string;
    graphSlug: string;
}>();

const options = ref<ReferenceSelectTreeNode[]>();
const isLoading = ref(false);
const optionsError = ref<string | null>(null);
const expandedKeys: Ref<TreeExpandedKeys> = ref({});

const initialVal = toRef(
    extractInitialOrDefaultValue(
        props.configuration.multiValue,
        props.initialValue,
        props.configuration.defaultValue,
    ),
);

function extractInitialOrDefaultValue(
    multiVal: boolean,
    initialVal: ReferenceSelectFetchedOption[] | undefined,
    defaultVal: ReferenceSelectFetchedOption[] | undefined,
) {
    return multiVal
        ? initialVal
            ? initialVal?.map((reference) => formatValForPrimevue(reference))
            : defaultVal?.map((reference) => formatValForPrimevue(reference))
        : initialVal
          ? formatValForPrimevue(initialVal ? initialVal[0] : undefined)
          : formatValForPrimevue(defaultVal ? defaultVal[0] : undefined);
}

function formatValForPrimevue(val: ReferenceSelectFetchedOption | undefined) {
    if (!val) {
        return undefined;
    }
    return { [val?.list_item_id]: true };
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

function resolver({ values }: FormFieldResolverOptions) {
    validate(values);
    // return new Promise((resolve) => {
    //     if (timeout) clearTimeout(timeout);

    //     timeout = setTimeout(() => {
    //         resolve(validate(e));
    //     }, 500);
    // });
    const nodeAlias = props.nodeAlias;
    let selectedItemKeys: string[] = [];
    if (values) {
        selectedItemKeys = Object.entries(values).reduce<string[]>(
            (keys, [key, val]) => {
                if (val === true) keys.push(key);
                return keys;
            },
            [],
        );
    }
    return {
        values: { [nodeAlias]: selectedItemKeys },
    };
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

onMounted(() => {
    options.value = [
        ...optionsAsNodes(props.initialValue ? props.initialValue : []),
        ...optionsAsNodes(
            props.configuration.defaultValue
                ? props.configuration.defaultValue
                : [],
        ),
    ];
});
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
