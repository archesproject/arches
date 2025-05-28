<script setup lang="ts">
import { ref, watchEffect } from "vue";

import Message from "primevue/message";
import ProgressSpinner from "primevue/progressspinner";

import NonLocalizedStringWidgetEditor from "@/arches_component_lab/widgets/NonLocalizedStringWidget/components/NonLocalizedStringWidgetEditor.vue";
import NonLocalizedStringWidgetViewer from "@/arches_component_lab/widgets/NonLocalizedStringWidget/components/NonLocalizedStringWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";
import { fetchCardXNodeXWidgetData } from "@/arches_component_lab/widgets/api.ts";

import type { CardXNodeXWidget } from "@/arches_component_lab/types.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

const props = withDefaults(
    defineProps<{
        mode: WidgetMode;
        nodeAlias: string;
        graphSlug: string;
        cardXNodeXWidgetData?: CardXNodeXWidget;
        initialValue?: string | null;
        showLabel?: boolean;
    }>(),
    {
        showLabel: true,
        cardXNodeXWidgetData: undefined,
    },
);

const isLoading = ref();
const cardXNodeXWidgetData = ref(props.cardXNodeXWidgetData);
const configurationError = ref();

watchEffect(async () => {
    if (props.cardXNodeXWidgetData) {
        return;
    }

    isLoading.value = true;

    try {
        cardXNodeXWidgetData.value = await fetchCardXNodeXWidgetData(
            props.nodeAlias,
            props.graphSlug,
        );
    } catch (error) {
        configurationError.value = error;
    } finally {
        isLoading.value = false;
    }
});
</script>

<template>
    <div class="widget">
        <ProgressSpinner
            v-if="isLoading"
            style="width: 2em; height: 2em"
        />
        <Message
            v-else-if="configurationError"
            severity="error"
            size="small"
        >
            {{ configurationError.message }}
        </Message>
        <template v-else>
            <label v-if="props.showLabel">
                <span>{{ cardXNodeXWidgetData.label }}</span>
                <span
                    v-if="
                        cardXNodeXWidgetData.node.isrequired &&
                        props.mode === EDIT
                    "
                    >*</span
                >
            </label>

            <div :class="[nodeAlias, graphSlug].join(' ')">
                <NonLocalizedStringWidgetEditor
                    v-if="mode === EDIT"
                    :initial-value="initialValue"
                    :graph-slug="props.graphSlug"
                    :node-alias="props.nodeAlias"
                />
                <NonLocalizedStringWidgetViewer
                    v-else-if="props.mode === VIEW"
                    :value="props.initialValue"
                />
            </div>
        </template>
    </div>
</template>

<style scoped>
.widget {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    width: 100%;
}
</style>
