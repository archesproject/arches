<script setup lang="ts">
import { inject } from "vue";
import { useGettext } from "vue3-gettext";

import InputSwitch from "primevue/inputswitch";
import { useToast } from "primevue/usetoast";

import { ARCHES_CHROME_BLUE } from "@/app/arches/theme.ts";
import { patchItem } from "@/controlled-lists/api.ts";
import {
    DEFAULT_ERROR_TOAST_LIFE,
    ERROR,
    itemKey,
} from "@/controlled-lists/constants.ts";

import type { Ref } from "vue";
import type { ControlledListItem } from "@/controlled-lists/types";

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
    }
};
</script>

<template>
    <div class="guide-container">
        <h4>{{ $gettext("Item Type") }}</h4>
        <p>{{ guideItemSubheading }}</p>
        <div class="guide-switch">
            <label for="guideSwitch">{{ $gettext("Guide item?") }}</label>
            <InputSwitch
                v-model="item.guide"
                input-id="guideSwitch"
                @change="issuePatchItem"
            />
        </div>
    </div>
</template>

<style scoped>
.guide-container {
    margin: 1rem 1rem 3rem 1rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    width: 100%;
    font-size: small;
}

.guide-switch {
    display: inline-flex;
    gap: 1rem;
    align-items: center;
}

label {
    /* Override arches.css */
    margin-bottom: 0;
}

h4 {
    color: v-bind(ARCHES_CHROME_BLUE);
    margin-top: 0;
    font-size: 1.33rem;
}

p {
    font-weight: normal;
    margin-top: 0;
    font-size: 1.2rem;
}
</style>
