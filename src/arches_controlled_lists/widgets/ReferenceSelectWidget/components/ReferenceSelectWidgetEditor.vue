<script setup lang="ts">
import { onMounted, ref, toRef } from "vue";

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
    nodeConfig: {
        multiValue: boolean;
        controlledList: string;
    };
    widgetConfig: {
        placeholder: string;
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
        props.nodeConfig.multiValue,
        props.initialValue,
        props.widgetConfig.defaultValue,
    ),
);

onMounted(() => {
    const defaultVal = props.widgetConfig.defaultValue;
    options.value = [
        ...optionsAsNodes(props.initialValue ? props.initialValue : []),
        ...optionsAsNodes(defaultVal ? defaultVal : []),
    ];
});

function extractInitialOrDefaultValue(
    multiVal: boolean,
    initialVal: ReferenceSelectFetchedOption[] | undefined,
    defaultVal: ReferenceSelectFetchedOption[] | undefined,
) {
    let extractedVals: object | undefined = undefined;
    if (multiVal) {
        if (initialVal) {
            extractedVals = initialVal?.map((reference) =>
                formatValForPrimevue(reference),
            );
        } else if (defaultVal) {
            extractedVals = defaultVal?.map((reference) =>
                formatValForPrimevue(reference),
            );
        }
    } else {
        if (initialVal && initialVal.length > 0) {
            extractedVals = formatValForPrimevue(initialVal[0]);
        } else if (defaultVal && defaultVal.length > 0) {
            extractedVals = formatValForPrimevue(defaultVal[0]);
        }
    }
    return extractedVals;
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
    if (items.length > 0) {
        return items.map(optionAsNode);
    }
    return [];
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

function resolver(options: FormFieldResolverOptions) {
    // return new Promise((resolve) => {
    //     if (timeout) clearTimeout(timeout);

    //     timeout = setTimeout(() => {
    //         resolve(validate(e));
    //     }, 500);
    // });
    const nodeAlias = props.nodeAlias;
    if (options.value) {
        options.value = Object.entries(options.value).reduce<string[]>(
            (keys, [key, val]) => {
                if (val === true) keys.push(key);
                return keys;
            },
            [],
        );
    }
    const { errors } = validate(options);
    return {
        errors,
        values: { [nodeAlias]: options.value },
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
    return { errors: [] };
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
            :placeholder="widgetConfig.placeholder"
            :selection-mode="nodeConfig.multiValue ? 'multiple' : 'single'"
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
