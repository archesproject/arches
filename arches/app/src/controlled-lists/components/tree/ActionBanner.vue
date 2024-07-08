<script setup lang="ts">
import { inject, ref } from "vue";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";

import { selectedLanguageKey } from "@/controlled-lists/constants.ts";
import { bestLabel } from "@/controlled-lists/utils.ts";

import type { Ref } from "vue";
import type { TreeSelectionKeys } from "primevue/tree/Tree";
import type { TreeNode } from "primevue/treenode";
import type { Language } from "@/arches/types";

const isMultiSelecting = defineModel<boolean>("isMultiSelecting", {
    required: true,
});
const movingItem = defineModel<TreeNode>("movingItem");
const rerenderTree = defineModel<number>("rerenderTree", { required: true });
const selectedKeys = defineModel<TreeSelectionKeys>("selectedKeys", {
    required: true,
});

const abandonMoveRef = ref();

const selectedLanguage = inject(selectedLanguageKey) as Ref<Language>;

const { $gettext } = useGettext();

const abandonMove = () => {
    movingItem.value = undefined;
    // Clear custom classes added in <Tree> pass-through
    rerenderTree.value += 1;
};
</script>

<template>
    <div
        v-if="movingItem"
        class="action-banner"
    >
        <!-- turn off escaping: vue template sanitizes -->
        {{
            $gettext(
                "Selecting new parent for: %{item}",
                {
                    item: bestLabel(movingItem.data, selectedLanguage.code)
                        .value,
                },
                true,
            )
        }}
        <Button
            ref="abandonMoveRef"
            type="button"
            class="banner-button"
            :label="$gettext('Abandon')"
            @click="abandonMove"
        />
    </div>
    <div
        v-else-if="isMultiSelecting"
        class="action-banner"
    >
        {{ $gettext("Select additional items to delete") }}
        <Button
            type="button"
            class="banner-button"
            :label="$gettext('Abandon')"
            @click="
                isMultiSelecting = false;
                selectedKeys = {};
            "
        />
    </div>
</template>

<style scoped>
.action-banner {
    background: yellow;
    font-weight: 800;
    height: 5rem;
    font-size: small;
    display: flex;
    justify-content: space-between;
    padding: 1rem;
    align-items: center;
}

.banner-button {
    height: 3rem;
    background: darkslategray;
    color: white;
    text-wrap: nowrap;
}
</style>
