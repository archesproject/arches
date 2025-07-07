<script setup lang="ts">
import { computed, defineAsyncComponent, ref, watchEffect } from "vue";

import Message from "primevue/message";
import Skeleton from "primevue/skeleton";

import GenericWidgetLabel from "@/arches_component_lab/widgets/GenericWidget/components/GenericWidgetLabel.vue";

import { fetchCardXNodeXWidgetData } from "@/arches_component_lab/widgets/api.ts";
import { getUpdatedComponentPath } from "@/arches_component_lab/widgets/utils.ts";

import type { CardXNodeXWidget } from "@/arches_component_lab/types.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

const props = withDefaults(
    defineProps<{
        cardXNodeXWidgetData?: CardXNodeXWidget;
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
const cardXNodeXWidgetData = ref(props.cardXNodeXWidgetData);
const configurationError = ref<Error>();

const widgetComponent = computed(() => {
    if (!cardXNodeXWidgetData.value) {
        return null;
    }

    const updatedComponentPath = getUpdatedComponentPath(
        cardXNodeXWidgetData.value.widget.component,
    );

    return defineAsyncComponent(() => import(`@/${updatedComponentPath}.vue`));
});

const value = computed(() => {
    if (props.value !== undefined) {
        return props.value;
    } else if (cardXNodeXWidgetData.value) {
        return cardXNodeXWidgetData.value.config.defaultValue;
    } else {
        return null;
    }
});

watchEffect(async () => {
    if (props.cardXNodeXWidgetData) {
        return;
    }

    isLoading.value = true;

    try {
        cardXNodeXWidgetData.value = await fetchCardXNodeXWidgetData(
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
        :graph-slug="graphSlug"
        :node-alias="nodeAlias"
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
        <template v-else-if="widgetComponent && cardXNodeXWidgetData">
            <label class="widget-label-container">
                <GenericWidgetLabel
                    v-if="shouldShowLabel"
                    :mode="mode"
                    :card-x-node-x-widget-data="cardXNodeXWidgetData"
                />

                <!-- Placing the component inside the label allows for inherit association with grandchild input -->
                <component
                    :is="widgetComponent"
                    :key="cardXNodeXWidgetData.id"
                    :card-x-node-x-widget-data="cardXNodeXWidgetData"
                    :graph-slug="graphSlug"
                    :mode="mode"
                    :node-alias="nodeAlias"
                    :value="value"
                    @update:value="emit('update:value', $event)"
                    @update:is-dirty="emit('update:isDirty', $event)"
                />
            </label>
        </template>
    </div>
</template>

<style scoped>
.widget {
    display: flex;
    flex-direction: column;
}
.widget-label {
    display: flex;
    cursor: pointer;
}
.widget-label-container {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}
</style>
