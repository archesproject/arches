<script setup lang="ts">
import {
    computed,
    defineAsyncComponent,
    ref,
    shallowRef,
    watch,
    watchEffect,
} from "vue";

import Message from "primevue/message";
import Skeleton from "primevue/skeleton";

import GenericWidgetLabel from "@/arches_component_lab/generics/GenericWidget/components/GenericWidgetLabel.vue";
import GenericFormField from "@/arches_component_lab/generics/GenericWidget/components/GenericFormField.vue";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";
import { useWidgetConfigStore } from "@/arches_component_lab/stores/useWidgetConfigStore.ts";
import { removeVueExtension } from "@/arches_component_lab/generics/GenericWidget/utils.ts";

import type {
    AliasedNodeData,
    CardXNodeXWidgetData,
} from "@/arches_component_lab/types.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

const {
    aliasedNodeData,
    cardXNodeXWidgetData,
    cardXNodeXWidgetDataOverrides,
    graphSlug,
    isDirty = false,
    mode,
    nodeAlias,
    shouldShowLabel = true,
    value,
} = defineProps<{
    aliasedNodeData?: AliasedNodeData | null | undefined;
    cardXNodeXWidgetData?: CardXNodeXWidgetData;
    cardXNodeXWidgetDataOverrides?: Partial<CardXNodeXWidgetData>;
    graphSlug: string;
    isDirty?: boolean;
    mode: WidgetMode;
    nodeAlias: string;
    shouldShowLabel?: boolean;
    value?: unknown | null | undefined;
}>();

const emit = defineEmits([
    "update:isDirty",
    "update:isFocused",
    "update:isLoading",
    "update:value",
    "update:aliasedNodeData",
    "initialized",
]);

defineOptions({ inheritAttrs: false });

const isLoading = ref(false);
const isChildLoading = ref(false);
const isWidgetInitialized = ref(false);
const resolvedInitialValue = ref<AliasedNodeData | null>(null);
const resolvedCardXNodeXWidgetData = shallowRef(cardXNodeXWidgetData);
const configurationError = ref<Error>();

const isCombinedLoading = computed(
    () => isLoading.value || isChildLoading.value,
);

const shouldShowSkeleton = computed(
    () =>
        isLoading.value ||
        (mode === EDIT &&
            resolvedCardXNodeXWidgetData.value &&
            !isWidgetInitialized.value),
);

const shouldShowWidget = computed(
    () =>
        !isLoading.value &&
        !configurationError.value &&
        widgetComponent.value &&
        resolvedCardXNodeXWidgetData.value,
);

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

const widgetNodeValue = computed<unknown>(() => {
    if (aliasedNodeData !== undefined) {
        return aliasedNodeData?.node_value ?? null;
    }
    if (value !== undefined) {
        return value ?? null;
    }
    return resolvedCardXNodeXWidgetData.value?.config?.defaultValue ?? null;
});

watch(isCombinedLoading, (newValue) => {
    emit("update:isLoading", newValue);
});

watch(
    () => resolvedCardXNodeXWidgetData.value?.id,
    () => {
        isWidgetInitialized.value = false;
    },
);

watchEffect(async () => {
    if (resolvedCardXNodeXWidgetData.value) {
        return;
    }

    isLoading.value = true;

    try {
        resolvedCardXNodeXWidgetData.value =
            await useWidgetConfigStore().fetchWidgetConfig(
                graphSlug,
                nodeAlias,
            );
        if (
            cardXNodeXWidgetDataOverrides &&
            resolvedCardXNodeXWidgetData.value
        ) {
            resolvedCardXNodeXWidgetData.value = {
                ...resolvedCardXNodeXWidgetData.value,
                ...cardXNodeXWidgetDataOverrides,
            };
        }
    } catch (error) {
        configurationError.value = error as Error;
    } finally {
        isLoading.value = false;
    }
});

function onWidgetInitialized(aliasedNodeData: AliasedNodeData) {
    isWidgetInitialized.value = true;
    resolvedInitialValue.value = aliasedNodeData;
    emit("initialized", aliasedNodeData);
}
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
            v-if="shouldShowSkeleton"
            style="height: 2rem"
        />
        <Message
            v-if="!isLoading && configurationError"
            severity="error"
            size="small"
        >
            {{ configurationError.message }}
        </Message>
        <template v-if="shouldShowWidget">
            <GenericWidgetLabel
                v-if="shouldShowLabel"
                :mode="mode"
                :card-x-node-x-widget-data="resolvedCardXNodeXWidgetData!"
            />

            <GenericFormField
                v-if="mode === EDIT"
                v-slot="{ onUpdateAliasedNodeData: notifyFormField }"
                :is-dirty="isDirty"
                :initial-value="resolvedInitialValue"
                :node-alias="nodeAlias"
                @update:is-dirty="emit('update:isDirty', $event)"
            >
                <div
                    v-show="isWidgetInitialized"
                    style="display: contents"
                >
                    <component
                        :is="widgetComponent"
                        v-bind="$attrs"
                        :key="resolvedCardXNodeXWidgetData!.id"
                        :aliased-node-data="aliasedNodeData"
                        :card-x-node-x-widget-data="
                            resolvedCardXNodeXWidgetData!
                        "
                        :graph-slug="graphSlug"
                        :mode="mode"
                        :node-alias="nodeAlias"
                        :value="widgetNodeValue"
                        @update:is-loading="isChildLoading = $event"
                        @update:value="emit('update:value', $event)"
                        @update:aliased-node-data="
                            (e: AliasedNodeData) => {
                                notifyFormField(e);
                                emit('update:aliasedNodeData', e);
                            }
                        "
                        @initialized="onWidgetInitialized"
                    />
                </div>
            </GenericFormField>

            <component
                :is="widgetComponent"
                v-else-if="mode === VIEW"
                v-bind="$attrs"
                :key="resolvedCardXNodeXWidgetData!.id"
                :aliased-node-data="aliasedNodeData"
                :card-x-node-x-widget-data="resolvedCardXNodeXWidgetData!"
                :graph-slug="graphSlug"
                :mode="mode"
                :node-alias="nodeAlias"
                :value="widgetNodeValue"
                @update:is-loading="isChildLoading = $event"
                @update:aliased-node-data="
                    emit('update:aliasedNodeData', $event)
                "
                @initialized="emit('initialized', $event)"
            />
        </template>
    </div>
</template>

<style scoped>
.widget {
    display: flex;
    flex-direction: column;
}
</style>
