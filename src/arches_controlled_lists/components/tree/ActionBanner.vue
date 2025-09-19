<script setup lang="ts">
import { inject } from "vue";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";
import ToggleSwitch from "primevue/toggleswitch";

import {
    selectedLanguageKey,
    systemLanguageKey,
    CONTRAST,
    SECONDARY,
} from "@/arches_controlled_lists/constants.ts";
import {
    getItemLabel,
    shouldUseContrast,
} from "@/arches_controlled_lists/utils.ts";

import type { Ref } from "vue";
import type { TreeSelectionKeys } from "primevue/tree";
import type { TreeNode } from "primevue/treenode";
import type { Language } from "@/arches_controlled_lists/types";

const isMultiSelecting = defineModel<boolean>("isMultiSelecting", {
    required: true,
});
const shouldCopyChildren = defineModel<boolean>("shouldCopyChildren", {
    required: true,
});
const movingItem = defineModel<TreeNode>("movingItem");
const rerenderTree = defineModel<number>("rerenderTree", { required: true });
const selectedKeys = defineModel<TreeSelectionKeys>("selectedKeys", {
    required: true,
});

const selectedLanguage = inject(selectedLanguageKey) as Ref<Language>;
const systemLanguage = inject(systemLanguageKey) as Language;

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
        <div class="action-banner-content">
            <!-- turn off escaping: vue template sanitizes -->
            {{
                $gettext(
                    "Selecting new parent for: %{item}",
                    {
                        item: getItemLabel(
                            movingItem.data,
                            selectedLanguage.code,
                            systemLanguage.code,
                        ).value,
                    },
                    true,
                )
            }}
            <Button
                type="button"
                class="banner-button"
                :severity="shouldUseContrast() ? CONTRAST : SECONDARY"
                :label="$gettext('Abandon')"
                @click="abandonMove"
            />
        </div>
        <div class="action-banner-content copy-children-option">
            <div class="value-editor-title">
                <label for="copyChildrenSwitch">
                    {{ $gettext("Include children (copy only)?") }}
                </label>
            </div>
            <div class="copy-children-switch">
                <ToggleSwitch
                    v-model="shouldCopyChildren"
                    input-id="copyChildrenSwitch"
                />
            </div>
        </div>
    </div>
    <div
        v-else-if="isMultiSelecting"
        class="action-banner action-banner-content"
    >
        {{ $gettext("Select additional items to delete") }}
        <Button
            type="button"
            class="banner-button"
            :severity="shouldUseContrast() ? CONTRAST : SECONDARY"
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
    background: var(--p-amber-300);
    color: var(--p-slate-950);
    font-weight: 800;
    font-size: small;
    padding: 1rem;
}

.action-banner-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.banner-button {
    height: 3rem;
    text-wrap: nowrap;
    font-size: unset;
    border-radius: 2px;
}

.action-banner-content.copy-children-option {
    padding-top: 0.5rem;
    gap: 1rem;
    justify-content: flex-start;
}

.value-editor-title label {
    cursor: pointer;
}
</style>
