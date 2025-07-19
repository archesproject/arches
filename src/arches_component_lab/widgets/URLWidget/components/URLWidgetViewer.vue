<script setup lang="ts">
import { useGettext } from "vue3-gettext";
import type { AliasedTileNodeValue } from "@/arches_component_lab/types.ts";
import type { URLDatatype } from "@/arches_component_lab/widgets/types.ts";

const { $gettext } = useGettext();

const { value } = defineProps<{
    value?: AliasedTileNodeValue | null | undefined;
}>();
</script>

<template>
    <a
        v-if="(value?.interchange_value as URLDatatype)?.url"
        :href="(value?.interchange_value as URLDatatype)?.url"
    >
        {{
            (value?.interchange_value as URLDatatype)?.url_label ||
            (value?.interchange_value as URLDatatype)?.url
        }}
    </a>

    <span v-else>
        {{ $gettext("No URL provided") }}
    </span>
</template>
