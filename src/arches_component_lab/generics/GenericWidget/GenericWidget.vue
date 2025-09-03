<script setup lang="ts">
import {
    computed,
    defineAsyncComponent,
    ref,
    shallowRef,
    watchEffect,
} from "vue";

import Message from "primevue/message";
import Skeleton from "primevue/skeleton";

import GenericWidgetLabel from "@/arches_component_lab/generics/GenericWidget/components/GenericWidgetLabel.vue";
import GenericFormField from "@/arches_component_lab/generics/GenericWidget/components/GenericFormField.vue";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";
import { fetchCardXNodeXWidgetData } from "@/arches_component_lab/generics/GenericWidget/api.ts";
import { removeVueExtension } from "@/arches_component_lab/generics/GenericWidget/utils.ts";

import type {
    AliasedNodeData,
    CardXNodeXWidgetData,
} from "@/arches_component_lab/types.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

const {
    cardXNodeXWidgetData,
    graphSlug,
    isDirty = false,
    mode,
    nodeAlias,
    shouldShowLabel = true,
    aliasedNodeData,
} = defineProps<{
    cardXNodeXWidgetData?: CardXNodeXWidgetData;
    graphSlug: string;
    isDirty?: boolean;
    mode: WidgetMode;
    nodeAlias: string;
    shouldShowLabel?: boolean;
    aliasedNodeData?: unknown | null | undefined;
}>();

const emit = defineEmits([
    "update:isDirty",
    "update:isFocused",
    "update:value",
]);

const isLoading = ref(false);
const resolvedCardXNodeXWidgetData = shallowRef(cardXNodeXWidgetData);
const configurationError = ref<Error>();

const widgetComponent = computed(() => {
    if (!resolvedCardXNodeXWidgetData.value) {
        return null;
    }

    return defineAsyncComponent(async () => {
        try {
            return await import(
                `@/${removeVueExtension(resolvedCardXNodeXWidgetData.value!.widget.component)}.vue`
            );
        } catch (err) {
            configurationError.value = err as Error;
        }
    });
});

const widgetValue = computed(() => {
    if (aliasedNodeData !== undefined) {
        return aliasedNodeData as AliasedNodeData;
    } else if (resolvedCardXNodeXWidgetData.value) {
        return resolvedCardXNodeXWidgetData.value.config
            .defaultValue as AliasedNodeData;
    } else {
        return null;
    }
});

watchEffect(async () => {
    if (resolvedCardXNodeXWidgetData.value) {
        return;
    }

    isLoading.value = true;

    try {
        resolvedCardXNodeXWidgetData.value = await fetchCardXNodeXWidgetData(
            graphSlug,
            nodeAlias,
        );
    } catch (error) {
        configurationError.value = error as Error;
    } finally {
        isLoading.value = false;
    }
});
</script>

<template>
    <div
        class="widget"
        :data-graph-slug="graphSlug"
        :data-node-alias="nodeAlias"
        @focusin="() => emit('update:isFocused', true)"
        @focusout="() => emit('update:isFocused', false)"
    >
        <Skeleton
            v-if="isLoading"
            style="height: 2rem"
        />
        <Message
            v-else-if="configurationError"
            severity="error"
            size="small"
        >
            {{ configurationError.message }}
        </Message>
        <template v-else-if="widgetComponent && resolvedCardXNodeXWidgetData">
            <GenericWidgetLabel
                v-if="shouldShowLabel"
                :mode="mode"
                :card-x-node-x-widget-data="resolvedCardXNodeXWidgetData"
            />

            <GenericFormField
                v-if="mode === EDIT"
                v-slot="{ onUpdateValue }"
                :aliased-node-data="widgetValue!"
                :is-dirty="isDirty"
                :node-alias="nodeAlias"
                @update:is-dirty="emit('update:isDirty', $event)"
                @update:value="emit('update:value', $event)"
            >
                <component
                    :is="widgetComponent"
                    :key="resolvedCardXNodeXWidgetData.id"
                    :card-x-node-x-widget-data="resolvedCardXNodeXWidgetData"
                    :graph-slug="graphSlug"
                    :mode="mode"
                    :node-alias="nodeAlias"
                    :aliased-node-data="widgetValue"
                    @update:value="onUpdateValue($event)"
                />
            </GenericFormField>

            <component
                :is="widgetComponent"
                v-else-if="mode === VIEW"
                :key="resolvedCardXNodeXWidgetData.id"
                :card-x-node-x-widget-data="resolvedCardXNodeXWidgetData"
                :graph-slug="graphSlug"
                :mode="mode"
                :node-alias="nodeAlias"
                :aliased-node-data="widgetValue"
            />
        </template>
    </div>
</template>

<style scoped>
.widget {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}
</style>
