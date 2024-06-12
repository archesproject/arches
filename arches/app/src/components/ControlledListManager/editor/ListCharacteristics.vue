<script setup lang="ts">
import { inject } from "vue";
import { useGettext } from "vue3-gettext";

import { displayedRowKey } from "@/components/ControlledListManager/constants.ts";
import LetterCircle from "@/components/ControlledListManager/misc/LetterCircle.vue";
import ListCharacteristic from "@/components/ControlledListManager/editor/ListCharacteristic.vue";
import ReferenceNodeLink from "@/components/ControlledListManager/editor/ReferenceNodeLink.vue";

import type { DisplayedListRefAndSetter } from "@/types/ControlledListManager";

const { displayedRow: list } = inject(
    displayedRowKey,
) as DisplayedListRefAndSetter;

const { $gettext } = useGettext();
</script>

<template>
    <template v-if="list">
        <span class="controlled-list-header">
            <LetterCircle
                v-if="list"
                :labelled="list"
            />
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
            <h4 class="nodes-heading">
                {{ $gettext("List used by these nodes") }}
            </h4>
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
    font-size: 1.6rem;
}

h4 {
    font-size: 1.33rem;
}

.nodes-heading {
    margin: 1rem 1rem 2rem 1rem;
}

.nodes {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    margin: 1rem;
}
</style>
