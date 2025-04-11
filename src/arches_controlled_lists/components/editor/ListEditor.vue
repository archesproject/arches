<script setup lang="ts">
import { inject } from "vue";
import { useGettext } from "vue3-gettext";

import { displayedRowKey } from "@/arches_controlled_lists/constants.ts";
import ListCharacteristic from "@/arches_controlled_lists/components/editor/ListCharacteristic.vue";
import ReferenceNodeLink from "@/arches_controlled_lists/components/editor/ReferenceNodeLink.vue";

import type { Ref } from "vue";
import type { ControlledList } from "@/arches_controlled_lists/types";

const { displayedRow: list } = inject(displayedRowKey) as unknown as {
    displayedRow: Ref<ControlledList>;
};

const { $gettext } = useGettext();
</script>

<template>
    <template v-if="list">
        <span class="controlled-list-header">
            <i
                class="pi pi-folder"
                :aria-label="$gettext('List')"
            ></i>
            <h3>{{ list.name }}</h3>
        </span>
        <div>
            <ListCharacteristic
                :editable="true"
                :label="$gettext('Name')"
            />
            <ListCharacteristic
                :editable="false"
                :label="$gettext('Dynamic')"
                :style="{ width: '4rem' }"
            />
            <div class="nodes-heading">
                <h4>{{ $gettext("List used by these nodes") }}</h4>
                <div class="nodes">
                    <div
                        v-for="node in list.nodes"
                        :key="node.id"
                    >
                        <ReferenceNodeLink :node />
                    </div>
                    <div
                        v-if="list.nodes.length === 0"
                        :style="{ fontSize: 'small' }"
                    >
                        {{ $gettext("None") }}
                    </div>
                </div>
            </div>
        </div>
    </template>
</template>

<style scoped>
.controlled-list-header {
    display: inline-flex;
    align-items: center;
    gap: 1rem;
    margin: 1rem 1rem 0rem 1rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid;
    width: 100%;
}

h3 {
    margin: 0;
}

.nodes-heading {
    margin: 1rem 1rem 2rem 1rem;
}

.nodes {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
}
</style>
