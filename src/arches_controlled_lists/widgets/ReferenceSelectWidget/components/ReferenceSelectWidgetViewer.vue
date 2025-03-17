<script setup lang="ts">
import type { ReferenceSelectFetchedOption } from "@/arches_controlled_lists/widgets/types";

defineProps<{
    value: ReferenceSelectFetchedOption[] | undefined;
}>();
</script>

<template>
    <template v-if="value">
        <span
            v-for="referenceItem in value"
            :key="referenceItem.list_item_id"
        >
            {{ referenceItem.display_value }}
        </span>
    </template>
    <span v-else>
        <span>{{ $gettext("None") }}</span>
    </span>
</template>
