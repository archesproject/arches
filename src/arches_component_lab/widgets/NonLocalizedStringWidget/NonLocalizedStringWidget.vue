<script setup lang="ts">
import { computed, ref, watchEffect } from "vue";

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
        cardXNodeXWidgetData: undefined,
        initialValue: undefined,
        showLabel: true,
    },
);

const isLoading = ref();
const cardXNodeXWidgetData = ref(props.cardXNodeXWidgetData);
const configurationError = ref();

const shouldShowRequiredAsterisk = computed(() => {
    return cardXNodeXWidgetData.value?.node.isrequired && props.mode === EDIT;
});

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
            <label
                v-if="props.showLabel"
                style="cursor: pointer; display: flex; margin-bottom: 0"
                :for="`${props.graphSlug}-${props.nodeAlias}-input`"
            >
                <div
                    v-tooltip="{
                        value: $gettext('This field is required.'),
                        disabled: !shouldShowRequiredAsterisk,
                        pt: {
                            arrow: {
                                style: {
                                    display: 'none',
                                },
                            },
                            text: {
                                style: {
                                    fontSize: '1rem',
                                    paddingBottom: '0.75rem',
                                    paddingInlineStart: '0.25rem',
                                },
                            },
                        },
                    }"
                    style="display: flex"
                >
                    <span>{{ cardXNodeXWidgetData.label }}</span>
                    <i
                        v-if="shouldShowRequiredAsterisk"
                        class="pi pi-asterisk"
                        style="font-size: 0.75rem; padding-top: 0.25rem"
                    />
                </div>
            </label>

            <div :class="[graphSlug, nodeAlias].join(' ')">
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
