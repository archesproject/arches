<script setup lang="ts">
import type { ControlledListItem } from "@/arches_controlled_lists/types.ts";

defineProps<{
    value: ControlledListItem[] | undefined;
    configuration: unknown;
}>();
</script>

<template>
    <template v-if="value">
        <span
            v-for="controlledListItem in value"
            :key="controlledListItem.list_id"
        >
            {{
                // @ts-expect-error
                controlledListItem.labels[0].value
            }}
        </span>
    </template>
    <span v-else>
        <span>{{ $gettext("None") }}</span>
    </span>
</template>
