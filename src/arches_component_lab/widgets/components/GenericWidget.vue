<script setup lang="ts">
import { computed, ref, watchEffect } from "vue";

import Message from "primevue/message";
import Skeleton from "primevue/skeleton";

import { fetchCardXNodeXWidgetData } from "@/arches_component_lab/widgets/api.ts";

import {
    CONFIGURE,
    EDIT,
    VIEW,
} from "@/arches_component_lab/widgets/constants.ts";

import type { CardXNodeXWidget } from "@/arches_component_lab/types.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

const props = withDefaults(
    defineProps<{
        cardXNodeXWidgetData?: CardXNodeXWidget;
        graphSlug: string;
        mode: WidgetMode;
        nodeAlias: string;
        showLabel?: boolean;
    }>(),
    {
        cardXNodeXWidgetData: undefined,
        showLabel: true,
    },
);

const isLoading = ref(false);
const cardXNodeXWidgetData = ref(props.cardXNodeXWidgetData);
const configurationError = ref<Error>();

const shouldShowRequiredAsterisk = computed(() => {
    return Boolean(
        props.mode === EDIT && cardXNodeXWidgetData.value?.node.isrequired,
    );
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
        <template v-else>
            <label
                v-if="showLabel"
                style="cursor: pointer; display: flex; margin-bottom: 0"
                :for="`${graphSlug}-${nodeAlias}-input`"
            >
                <div
                    v-tooltip="{
                        value: $gettext('This field is required.'),
                        disabled: !shouldShowRequiredAsterisk,
                        pt: {
                            arrow: {
                                style: { display: 'none' },
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
                        aria-hidden="true"
                        class="pi pi-asterisk"
                        style="font-size: 0.75rem; padding-top: 0.25rem"
                    />
                </div>
            </label>

            <div>
                <slot
                    v-if="mode === CONFIGURE"
                    name="configurator"
                    :card-x-node-x-widget-data="cardXNodeXWidgetData"
                />
                <slot
                    v-else-if="mode === EDIT"
                    name="editor"
                    :card-x-node-x-widget-data="cardXNodeXWidgetData"
                />
                <slot
                    v-else-if="mode === VIEW"
                    name="viewer"
                    :card-x-node-x-widget-data="cardXNodeXWidgetData"
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
