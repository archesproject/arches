<script setup lang="ts">
import { inject } from "vue";
import { useGettext } from "vue3-gettext";

import LetterCircle from "@/components/ControlledListManager/LetterCircle.vue";
import ListCharacteristic from "@/components/ControlledListManager/ListCharacteristic.vue";
import ReferenceNodeLink from "@/components/ControlledListManager/ReferenceNodeLink.vue";
import { displayedRowKey } from "@/components/ControlledListManager/const.ts";

const { displayedRow } = inject(displayedRowKey);

const { $gettext } = useGettext();
</script>

<template>
    <span class="controlled-list-header">
        <LetterCircle
            v-if="displayedRow"
            :labelled="displayedRow"
        />
        <h3>{{ displayedRow.name }}</h3>
    </span>
    <div>
        <ListCharacteristic
            :editable="true"
            field="name"
            :label="$gettext('Name')"
        />
        <ListCharacteristic
            :editable="false"
            field="dynamic"
            :label="$gettext('Dynamic')"
            :style="{ width: '4rem' }"
        />
        <h4 class="nodes-heading">
            {{ $gettext("List used by these nodes") }}
        </h4>
        <div class="nodes">
            <div
                v-for="node in displayedRow.nodes"
                :key="node.id"
            >
                <ReferenceNodeLink :node />
            </div>
            <div
                v-if="displayedRow.nodes.length === 0"
                :style="{ fontSize: 'small' }"
            >
                {{ $gettext('None') }}
            </div>
        </div>
    </div>
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
    font-size: 1.5rem;
}

h4 {
    font-size: 1.25rem;
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
