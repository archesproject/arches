<script setup lang="ts">
import { useGettext } from "vue3-gettext";

import ItemCharacteristic from "@/components/ControlledListManager/ItemCharacteristic.vue";
import ReferenceNodeLink from "@/components/ControlledListManager/ReferenceNodeLink.vue";

import type { ControlledList } from "@/types/ControlledListManager";

const props: {
    displayedList: ControlledList;
    editable: boolean;
} = defineProps([
    "displayedList",
    "editable",
]);

const { $gettext } = useGettext();
const LIST_DETAILS = $gettext("List Details");
</script>

<template>
    <h3>{{ LIST_DETAILS }}</h3>
    <div class="characteristics">
        <ItemCharacteristic
            :item="props.displayedList"
            :editable="props.editable"
            field="name"
            :label="$gettext('Name')"
        />
        <ItemCharacteristic
            :item="props.displayedList"
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
                v-for="node in props.displayedList.nodes"
                :key="node.id"
            >
                <ReferenceNodeLink :node />
            </div>
        </div>
    </div>
</template>

<style scoped>
h3 {
    font-size: 1.5rem;
    margin: 1rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid;
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
