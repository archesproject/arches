<script setup lang="ts">
import { useGettext } from "vue3-gettext";
import type { URLValue } from "@/arches_component_lab/datatypes/url/types.ts";

const { $gettext } = useGettext();

defineProps<{
    value: URLValue;
}>();
</script>

<template>
    <a
        v-if="value?.node_value.url"
        :href="value?.node_value.url"
    >
        {{ value?.node_value?.url_label || value?.node_value?.url }}
    </a>

    <span v-else>
        {{ $gettext("No URL provided") }}
    </span>
</template>
