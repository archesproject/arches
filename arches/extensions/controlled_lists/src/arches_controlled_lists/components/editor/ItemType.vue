<script setup lang="ts">
import { inject } from "vue";
import { useGettext } from "vue3-gettext";

import ToggleSwitch from "primevue/toggleswitch";
import { useToast } from "primevue/usetoast";

import { patchItem } from "@/arches_controlled_lists/api.ts";
import {
    DEFAULT_ERROR_TOAST_LIFE,
    ERROR,
    itemKey,
} from "@/arches_controlled_lists/constants.ts";

import type { Ref } from "vue";
import type { ControlledListItem } from "@/arches_controlled_lists/types";

const item = inject(itemKey) as Ref<ControlledListItem>;
const toast = useToast();
const { $gettext } = useGettext();

const guide = "guide";
const guideItemSubheading = $gettext(
    "If this item should only display as an intermediate grouping in the list hierarchy, mark it as a guide item to prevent it from being chosen by a user.",
);

const issuePatchItem = async () => {
    try {
        await patchItem(item.value, guide);
    } catch (error) {
        toast.add({
            severity: ERROR,
            life: DEFAULT_ERROR_TOAST_LIFE,
            summary: $gettext("Save failed"),
            detail: error instanceof Error ? error.message : undefined,
        });
        item.value.guide = !item.value.guide;
    }
};
</script>

<template>
    <div class="guide-container">
        <h4>{{ $gettext("Item Type") }}</h4>
        <p>{{ guideItemSubheading }}</p>
        <div class="guide-switch">
            <label for="guideSwitch">{{ $gettext("Guide item?") }}</label>
            <ToggleSwitch
                v-model="item.guide"
                input-id="guideSwitch"
                @change="issuePatchItem"
            />
        </div>
    </div>
</template>

<style scoped>
.guide-container {
    margin: 1rem 1rem 4rem 2rem;
    display: flex;
    flex-direction: column;
    gap: 0;
}

.guide-container h4 {
    font-size: 1.66rem;
    margin: 0;
    padding: 0.5rem 0 0 0;
    font-weight: 400;
}

.guide-container p {
    margin: 0;
    padding: 0.25rem 0 0 0;
    color: var(--p-text-muted-color);
}

.guide-switch {
    display: inline-flex;
    gap: 1rem;
    padding: 0.5rem 0 0 0;
    align-items: center;
}

label {
    /* Override arches.css */
    margin-bottom: 0;
}

h4 {
    margin-top: 0;
}

p {
    font-weight: normal;
    margin-top: 0;
}
</style>
