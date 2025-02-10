<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";

import Select from "primevue/select";

import { fetchLists } from "@/arches_component_lab/widgets/api.ts";

const props = defineProps<{
    initialValue: any;
    configuration: any;
}>();

const rawValue = ref(props.initialValue[0].uri);
const isDirty = computed(() => rawValue.value !== props.initialValue[0].uri);

const options = ref([]);

defineExpose({
    rawValue,
    isDirty,
});

onMounted(async () => {
    options.value = await getOptions();
});

// THE API THIS FUNCTION INTERACTS WITH SHOULD BE UPDATED
// TO PROVIDE THE MOST SIMPLE LIST OF CONTROLLED LIST OPTIONS
async function getOptions() {
    let fetchedLists;
    try {
        fetchedLists = await fetchLists([props.configuration.nodeAlias]);
    } catch (error) {
        // NO TOAST! INSTEAD RENDER ERROR MESSAGE COMPONENT
        // NO GETTEXT! SHOULD JUST RENDER SERVER RESPONSE
        // toast.add({
        //     severity: "error",
        //     summary: $gettext("Error"),
        //     detail:
        //         error instanceof Error
        //             ? error.message
        //             : $gettext("Could not fetch the controlled list options"),
        // });
        // return [];
    }

    console.log(fetchedLists);
    const controlledList = fetchedLists.controlled_lists[0];

    return controlledList.items.map((item) => ({
        list_id: item.list_id,
        uri: item.uri,
        labels: item.values,
    }));
}

function extractURI(item: ControlledListItem[]): string | string[] {
    if (item && !props.multiValue) {
        return item[0]?.uri;
    } else if (item && props.multiValue) {
        return item.map((item) => item.uri);
    } else {
        return [];
    }
}

// THIS SHOULD NOT EXIST, THE API SHOULD RETURN A MORE SIMPLIFIED RESPONSE
function getOptionLabels(item: ControlledListItem): string {
    const prefLabels = item.labels.filter(
        (label) => label.valuetype_id === "prefLabel",
    );
    const optionLabel =
        prefLabels.find((label) => label.language_id === "en") || prefLabels[0];
    return optionLabel?.value ?? "";
}
</script>

<template>
    <Select
        v-model="rawValue"
        style="display: flex"
        option-value="uri"
        :options="options"
        :option-label="getOptionLabels"
        :placeholder="configuration.placeholder"
    />
</template>
