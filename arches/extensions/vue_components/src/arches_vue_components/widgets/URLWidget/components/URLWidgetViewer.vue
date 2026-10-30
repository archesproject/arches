<script setup lang="ts">
import { useGettext } from "vue3-gettext";

import type { URLAliasedNodeData } from "@/arches_vue_components/datatypes/url/types.ts";

defineProps<{
    aliasedNodeData: URLAliasedNodeData;
}>();

const { $gettext } = useGettext();
</script>

<template>
    <a
        v-if="aliasedNodeData?.node_value?.url"
        :href="aliasedNodeData.node_value.url"
    >
        {{
            aliasedNodeData.node_value.url_label ||
            aliasedNodeData.node_value.url
        }}
    </a>

    <span v-else>
        {{ $gettext("No URL provided") }}
    </span>
</template>
