<script setup lang="ts">
import { computed, inject, ref } from "vue";

import { useGettext } from "vue3-gettext";

import Badge from "openvue/badge";
import Button from "openvue/button";

import OverlaySwatch from "@/arches_vue_components/components/MapComponent/components/OverlaySwatch.vue";

import { panelHeaderActionsIdKey } from "@/arches_vue_components/components/MapComponent/constants.ts";
import { useResolvedMapContext } from "@/arches_vue_components/components/MapComponent/composables/useMapContext.ts";
import { getOverlayOpacityPercent } from "@/arches_vue_components/components/MapComponent/utils/overlay-opacity.ts";

import type {
    MapContext,
    MapLayer,
} from "@/arches_vue_components/components/MapComponent/types.ts";

const RESOURCE_LAYERS_GROUP_ID = "resource-layers";
const OVERLAYS_GROUP_ID = "overlays";

const { context = undefined } = defineProps<{
    context?: MapContext;
}>();

const panelHeaderActionsId = inject(panelHeaderActionsIdKey, null);

const { overlays, overlayOpacities } = useResolvedMapContext(
    context,
    "LegendPanel",
);

const { $gettext } = useGettext();

const collapsedGroupIds = ref<string[]>([]);

const visibleGroups = computed(() => {
    const visibleOverlays = overlays.value.filter(
        (overlay) => overlay.addtomap,
    );
    const groups = [
        {
            id: RESOURCE_LAYERS_GROUP_ID,
            label: $gettext("Resource geometries"),
            overlays: visibleOverlays.filter(
                (overlay) => overlay.is_resource_layer,
            ),
        },
        {
            id: OVERLAYS_GROUP_ID,
            label: $gettext("Overlays"),
            overlays: visibleOverlays.filter(
                (overlay) => !overlay.is_resource_layer,
            ),
        },
    ];
    return groups.filter((group) => group.overlays.length);
});

const areAllGroupsCollapsed = computed(() =>
    visibleGroups.value.every((group) =>
        collapsedGroupIds.value.includes(group.id),
    ),
);

const headerActionsSelector = computed(() => {
    if (!panelHeaderActionsId) {
        return "body";
    }
    return `#${panelHeaderActionsId}`;
});

const toggleAllGroupsIcon = computed(() => {
    if (areAllGroupsCollapsed.value) {
        return "pi pi-angle-double-down";
    }
    return "pi pi-angle-double-up";
});

const toggleAllGroupsLabel = computed(() => {
    if (areAllGroupsCollapsed.value) {
        return $gettext("Expand all groups");
    }
    return $gettext("Collapse all groups");
});

function isGroupCollapsed(groupId: string): boolean {
    return collapsedGroupIds.value.includes(groupId);
}

function toggleGroup(groupId: string): void {
    if (isGroupCollapsed(groupId)) {
        collapsedGroupIds.value = collapsedGroupIds.value.filter(
            (collapsedGroupId) => collapsedGroupId !== groupId,
        );
    } else {
        collapsedGroupIds.value.push(groupId);
    }
}

function toggleAllGroups(): void {
    if (areAllGroupsCollapsed.value) {
        collapsedGroupIds.value = [];
    } else {
        collapsedGroupIds.value = visibleGroups.value.map((group) => group.id);
    }
}

function getOpacityPercent(overlay: MapLayer): number {
    return getOverlayOpacityPercent(overlayOpacities.value, overlay);
}
</script>

<template>
    <Teleport
        v-if="visibleGroups.length"
        :to="headerActionsSelector"
        :disabled="!panelHeaderActionsId"
        :defer="true"
    >
        <div class="legend-actions">
            <Button
                severity="secondary"
                :icon="toggleAllGroupsIcon"
                :text="true"
                :rounded="true"
                :aria-label="toggleAllGroupsLabel"
                @click="toggleAllGroups"
            />
        </div>
    </Teleport>
    <div class="legend-groups">
        <div
            v-if="!visibleGroups.length"
            class="legend-empty"
        >
            <i
                class="pi pi-eye-slash"
                aria-hidden="true"
            />
            <span>
                {{
                    $gettext(
                        "No layers currently visible. Switch to the Overlays panel to turn some on.",
                    )
                }}
            </span>
        </div>
        <section
            v-for="group in visibleGroups"
            :key="group.id"
            class="legend-group"
        >
            <Button
                class="legend-group-header"
                :class="{
                    'legend-group-header-collapsed': isGroupCollapsed(group.id),
                }"
                :text="true"
                :aria-expanded="!isGroupCollapsed(group.id)"
                @click="toggleGroup(group.id)"
            >
                <i
                    class="pi pi-chevron-down legend-group-chevron"
                    aria-hidden="true"
                />
                <span class="legend-group-label">{{ group.label }}</span>
                <Badge
                    severity="secondary"
                    :value="group.overlays.length"
                />
            </Button>
            <template v-if="!isGroupCollapsed(group.id)">
                <div
                    v-for="overlay in group.overlays"
                    :key="overlay.maplayerid"
                    class="legend-row"
                >
                    <!-- eslint-disable vue/no-v-html -->
                    <div
                        v-if="overlay.legend"
                        class="legend-html"
                        v-html="overlay.legend"
                    />
                    <!-- eslint-enable vue/no-v-html -->
                    <template v-else>
                        <OverlaySwatch
                            :overlay="overlay"
                            :opacity-percent="getOpacityPercent(overlay)"
                        />
                        <span
                            class="legend-label"
                            :title="overlay.name"
                        >
                            {{ overlay.name }}
                        </span>
                    </template>
                </div>
            </template>
        </section>
    </div>
    <div class="legend-footnote">
        {{
            $gettext(
                "Read-only — every entry mirrors an overlay currently switched on in Overlays. Toggle something off there and it disappears from here immediately.",
            )
        }}
    </div>
</template>

<style scoped>
.legend-actions {
    display: flex;
    justify-content: flex-end;
}

.legend-groups {
    flex: 1;
    overflow-y: auto;
}

.legend-empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.8rem;
    padding-block: 2.4rem;
    padding-inline: 1.6rem;
    color: var(--p-text-muted-color);
    font-size: 1.3rem;
    line-height: 1.5;
    text-align: center;
}

.legend-empty .pi {
    font-size: 2.2rem;
    opacity: 0.5;
}

.legend-group {
    border-block-end: 0.1rem solid var(--p-content-border-color);
}

.legend-group:last-child {
    border-block-end: none;
}

.legend-group-header {
    justify-content: flex-start;
    gap: 0.65rem;
    width: 100%;
    padding-block: 0.8rem;
    padding-inline: 1.6rem;
    border-radius: 0;
    background: var(--p-content-hover-background);
    color: var(--p-text-muted-color);
    font-size: 1.2rem;
    font-weight: 700;
    letter-spacing: 0.05rem;
    text-transform: uppercase;
}

.legend-group-chevron {
    font-size: 1rem;
    transition: transform 0.15s ease;
}

.legend-group-header-collapsed .legend-group-chevron {
    transform: rotate(-90deg);
}

.legend-group-label {
    flex: 1;
    text-align: start;
}

.legend-row {
    display: flex;
    align-items: center;
    gap: 0.9rem;
    padding-block: 0.8rem;
    padding-inline: 2.4rem 1.6rem;
}

.legend-row:hover {
    background: var(--p-content-hover-background);
}

.legend-html {
    flex: 1;
    min-width: 0;
    font-size: 1.35rem;
    line-height: 1.35;
}

.legend-label {
    flex: 1;
    min-width: 0;
    overflow: hidden;
    font-size: 1.35rem;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.legend-footnote {
    flex: 0 0 auto;
    padding-block: 1rem;
    padding-inline: 1.6rem;
    border-block-start: 0.1rem solid var(--p-content-border-color);
    background: var(--p-content-hover-background);
    color: var(--p-text-muted-color);
    font-size: 1.15rem;
    line-height: 1.4;
}
</style>
