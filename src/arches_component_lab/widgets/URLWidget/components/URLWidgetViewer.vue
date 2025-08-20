<script setup lang="ts">
import { useGettext } from "vue3-gettext";
import type { URLValue } from "@/arches_component_lab/datatypes/url/types.ts";

const { $gettext } = useGettext();

defineProps<{
    aliasedNodeData: URLValue;
}>();
</script>

<template>
    <a
        v-if="aliasedNodeData?.node_value.url"
        :href="aliasedNodeData?.node_value.url"
    >
        {{
            aliasedNodeData?.node_value?.url_label ||
            aliasedNodeData?.node_value?.url
        }}
    </a>

    <span v-else>
        {{ $gettext("No URL provided") }}
    </span>
</template>
