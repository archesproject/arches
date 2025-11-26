<script setup lang="ts">
import {
    reactive,
    toRaw,
    ref,
    watch,
    nextTick,
    useTemplateRef,
    computed,
} from "vue";
import { useGettext } from "vue3-gettext";

import { Form } from "@primevue/forms";
import Button from "primevue/button";
import Message from "primevue/message";
import Skeleton from "primevue/skeleton";

import GenericWidget from "@/arches_component_lab/generics/GenericWidget/GenericWidget.vue";
import { upsertTile } from "@/arches_component_lab/generics/GenericCard/api.ts";

import type {
    AliasedNodeData,
    AliasedTileData,
    CardXNodeXWidgetData,
} from "@/arches_component_lab/types.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

const { $gettext } = useGettext();

const SAVE = $gettext("Save");
const CANCEL = $gettext("Cancel");

const {
    cardXNodeXWidgetData,
    graphSlug,
    mode,
    nodegroupAlias,
    resourceInstanceId,
    selectedNodeAlias,
    shouldShowFormButtons = true,
    tileData,
} = defineProps<{
    cardXNodeXWidgetData: CardXNodeXWidgetData[];
    graphSlug: string;
    mode: WidgetMode;
    nodegroupAlias: string;
    resourceInstanceId: string | null | undefined;
    selectedNodeAlias?: string | null;
    shouldShowFormButtons: boolean | undefined;
    tileData?: AliasedTileData;
}>();

const emit = defineEmits([
    "update:tileData",
    "update:widgetDirtyStates",
    "update:widgetFocusStates",
    "save",
    "reset",
]);

function deepClone<T>(sourceObject: T): T {
    return JSON.parse(JSON.stringify(sourceObject));
}

const genericWidgetRefs = useTemplateRef("genericWidget");

const formKey = ref(0);
const isSaving = ref(false);
const saveError = ref<Error>();

const originalAliasedData = deepClone(tileData?.aliased_data || {});
const aliasedData = reactive(deepClone(tileData?.aliased_data || {}));

const localWidgetDirtyStates = reactive(
    cardXNodeXWidgetData.reduce<Record<string, boolean>>(
        (dirtyStatesMap, widgetDatum) => {
            dirtyStatesMap[widgetDatum.node.alias] = false;
            return dirtyStatesMap;
        },
        {},
    ),
);

const localWidgetFocusedStates = reactive(
    cardXNodeXWidgetData.reduce<Record<string, boolean>>(
        (focusedStatesMap, widgetDatum) => {
            focusedStatesMap[widgetDatum.node.alias] = false;
            return focusedStatesMap;
        },
        {},
    ),
);

const areButtonsDisabled = computed(() => {
    return Object.values(localWidgetDirtyStates).every(
        (isWidgetDirty) => !isWidgetDirty,
    );
});

async function focusWidgetInputForNodeAlias(nodeAlias: string) {
    for (let attemptCount = 0; attemptCount < 5; attemptCount += 1) {
        const widgetComponentRefs = genericWidgetRefs.value;
        if (!Array.isArray(widgetComponentRefs)) {
            return;
        }

        const activeElement = document.activeElement as HTMLElement | null;

        for (const widgetComponentRef of widgetComponentRefs) {
            const widgetRootElement =
                widgetComponentRef?.$el as HTMLElement | null;

            if (!widgetRootElement) {
                continue;
            }

            if (activeElement && widgetRootElement.contains(activeElement)) {
                return;
            }

            const inputElementToFocus =
                widgetRootElement.querySelector<HTMLElement>(`#${nodeAlias}`);

            if (inputElementToFocus) {
                inputElementToFocus.focus();
                return;
            }
        }

        await new Promise<void>((resolve) => {
            requestAnimationFrame(() => resolve());
        });
    }
}

watch(
    () => selectedNodeAlias,
    async (nodeAlias) => {
        if (!nodeAlias) {
            return;
        }

        await nextTick();
        await focusWidgetInputForNodeAlias(nodeAlias);
    },
    { immediate: true, flush: "post" },
);

watch(
    aliasedData,
    () => {
        emit("update:tileData", {
            ...tileData,
            aliased_data: toRaw(aliasedData),
        });
    },
    { deep: true },
);

watch(
    () => ({ ...localWidgetDirtyStates }),
    (newDirtyStatesMap) => {
        emit("update:widgetDirtyStates", newDirtyStatesMap);
    },
);

watch(
    () => ({ ...localWidgetFocusedStates }),
    (newFocusedStatesMap) => {
        emit("update:widgetFocusStates", newFocusedStatesMap);
    },
);

function onUpdateWidgetDirtyState(nodeAlias: string, isDirty: boolean) {
    localWidgetDirtyStates[nodeAlias] = isDirty;
}

function onUpdateWidgetFocusedState(nodeAlias: string, isFocused: boolean) {
    localWidgetFocusedStates[nodeAlias] = isFocused;
}

function onUpdateWidgetValue(nodeAlias: string, value: AliasedNodeData) {
    aliasedData[nodeAlias] = value;
}

function resetWidgetDirtyStates() {
    Object.keys(localWidgetDirtyStates).forEach((nodeAlias) => {
        localWidgetDirtyStates[nodeAlias] = false;
    });
}

function resetForm() {
    resetWidgetDirtyStates();

    const originalAliasedDataClone = deepClone(originalAliasedData);

    Object.assign(aliasedData, originalAliasedDataClone);
    formKey.value += 1;

    nextTick(() => {
        emit("reset", originalAliasedDataClone);
    });
}

async function save() {
    isSaving.value = true;
    saveError.value = undefined;

    try {
        const updatedTileData = await upsertTile(
            graphSlug,
            nodegroupAlias,
            {
                ...(tileData as AliasedTileData),
                aliased_data: toRaw(aliasedData),
            },
            tileData?.tileid ? tileData.tileid : undefined,
            resourceInstanceId,
        );

        Object.assign(aliasedData, deepClone(updatedTileData.aliased_data));
        Object.assign(
            originalAliasedData,
            deepClone(updatedTileData.aliased_data),
        );

        resetWidgetDirtyStates();

        nextTick(() => {
            emit("save", updatedTileData);
        });
    } catch (caughtError) {
        saveError.value = caughtError as Error;
    } finally {
        isSaving.value = false;
    }
}

defineExpose({ save });
</script>

<template>
    <Skeleton
        v-if="isSaving"
        style="height: 10rem"
    />
    <template v-else>
        <Message
            v-if="saveError"
            severity="error"
        >
            {{ saveError.message }}
        </Message>
        <Form
            :key="formKey"
            class="form"
        >
            <template
                v-for="cardXNodeXWidgetDatum in cardXNodeXWidgetData"
                :key="cardXNodeXWidgetDatum.id"
            >
                <GenericWidget
                    v-if="cardXNodeXWidgetDatum.visible"
                    ref="genericWidget"
                    :is-dirty="
                        localWidgetDirtyStates[cardXNodeXWidgetDatum.node.alias]
                    "
                    :card-x-node-x-widget-data="cardXNodeXWidgetDatum"
                    :graph-slug="graphSlug"
                    :mode="mode"
                    :node-alias="cardXNodeXWidgetDatum.node.alias"
                    :aliased-node-data="
                        aliasedData[cardXNodeXWidgetDatum.node.alias]
                    "
                    @update:is-dirty="
                        onUpdateWidgetDirtyState(
                            cardXNodeXWidgetDatum.node.alias,
                            $event,
                        )
                    "
                    @update:is-focused="
                        onUpdateWidgetFocusedState(
                            cardXNodeXWidgetDatum.node.alias,
                            $event,
                        )
                    "
                    @update:value="
                        onUpdateWidgetValue(
                            cardXNodeXWidgetDatum.node.alias,
                            $event,
                        )
                    "
                />
            </template>

            <div
                v-if="shouldShowFormButtons"
                class="form-action-buttons"
            >
                <Button
                    :disabled="areButtonsDisabled"
                    :loading="isSaving"
                    severity="success"
                    size="small"
                    icon="pi pi-check"
                    :label="SAVE"
                    @click="save"
                />
                <Button
                    :disabled="areButtonsDisabled"
                    type="button"
                    severity="warn"
                    size="small"
                    icon="pi pi-undo"
                    :label="CANCEL"
                    @click="resetForm"
                />
            </div>
        </Form>
    </template>
</template>

<style scoped>
.form {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.form-action-buttons {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
    padding-top: 1rem;
    flex-wrap: wrap;
}
</style>
