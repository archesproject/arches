<script setup lang="ts">
import { computed } from "vue";

import { VIEW } from "@/arches_component_lab/widgets/constants.ts";

import type { CardXNodeXWidget } from "@/arches_component_lab/types.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

const props = defineProps<{
    mode: WidgetMode;
    cardXNodeXWidgetData: CardXNodeXWidget;
}>();

const shouldShowRequiredAsterisk = computed(() => {
    return Boolean(
        props.mode !== VIEW && props.cardXNodeXWidgetData.node.isrequired,
    );
});
</script>

<template>
    <div class="widget-label">
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
    </div>
</template>

<style scoped>
.widget-label {
    display: flex;
    cursor: pointer;
}
</style>
