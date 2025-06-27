<script setup lang="ts">
import { useGettext } from "vue3-gettext";
import type { URLDatatype } from "@/arches_component_lab/widgets/types.ts";

const { $gettext } = useGettext();

const props = defineProps<{
    value?: URLDatatype | null | undefined;
}>();
</script>

<template>
    <a
        v-if="props.value?.url"
        :href="props.value.url"
    >
        {{ props.value.url_label || props.value.url }}
    </a>

    <span v-else>
        {{ $gettext("No URL provided") }}
    </span>
</template>
