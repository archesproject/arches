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

import { fetchCardXNodeXWidgetData } from "@/arches_component_lab/generics/GenericWidget/api.ts";
import { getUpdatedComponentPath } from "@/arches_component_lab/generics/GenericWidget/utils.ts";

import type { CardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

const props = withDefaults(
    defineProps<{
        cardXNodeXWidgetData?: CardXNodeXWidgetData;
        graphSlug: string;
        mode: WidgetMode;
        nodeAlias: string;
        shouldShowLabel?: boolean;
        value?: unknown | null | undefined;
    }>(),
    {
        cardXNodeXWidgetData: undefined,
        shouldShowLabel: true,
        value: undefined,
    },
);

const emit = defineEmits(["update:isDirty", "update:value"]);

const isLoading = ref(false);
const resolvedCardXNodeXWidgetData = shallowRef(props.cardXNodeXWidgetData);
const configurationError = ref<Error>();

const widgetComponent = computed(() => {
    if (!resolvedCardXNodeXWidgetData.value) {
        return null;
    }

    const updatedComponentPath = getUpdatedComponentPath(
        resolvedCardXNodeXWidgetData.value.widget.component,
    );

    return defineAsyncComponent(async () => {
        try {
            return await import(`@/${updatedComponentPath}.vue`);
        } catch (err) {
            configurationError.value = err as Error;
        }
    });
});

const widgetValue = computed(() => {
    if (props.value !== undefined) {
        return props.value;
    } else if (resolvedCardXNodeXWidgetData.value) {
        return resolvedCardXNodeXWidgetData.value.config.defaultValue;
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
            props.graphSlug,
            props.nodeAlias,
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
        <label
            v-else-if="widgetComponent && resolvedCardXNodeXWidgetData"
            class="widget-label-container"
        >
            <GenericWidgetLabel
                v-if="shouldShowLabel"
                :mode="mode"
                :card-x-node-x-widget-data="resolvedCardXNodeXWidgetData"
            />

            <!-- Placing the component inside the label allows for inherit association with grandchild input -->
            <component
                :is="widgetComponent"
                :key="resolvedCardXNodeXWidgetData.id"
                :card-x-node-x-widget-data="resolvedCardXNodeXWidgetData"
                :graph-slug="graphSlug"
                :mode="mode"
                :node-alias="nodeAlias"
                :value="widgetValue"
                @update:value="emit('update:value', $event)"
                @update:is-dirty="emit('update:isDirty', $event)"
            />
        </label>
    </div>
</template>

<style scoped>
.widget {
    display: flex;
    flex-direction: column;
}
.widget-label-container {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}
</style>
