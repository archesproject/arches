<script setup>
const staticLabel = "Static: list does not change";
const dynamicLabel =
    "Dynamic: list is defined by a query that may change list items";

const { displayedList } = defineProps(["displayedList"]);
</script>

<template>
    <div class="characteristics">
        <h4>Characteristics</h4>
        <div class="characteristic">
            <h5>Name</h5>
            <input
                disabled
                :value="displayedList.value.name"
                :style="{ width: displayedList.value.name.length + 'rem' }"
            />
        </div>
        <div class="characteristic">
            <h5>Type</h5>
            <input
                disabled
                :value="
                    displayedList.value.dynamic ? dynamicLabel : staticLabel
                "
                :style="{
                    width: displayedList.value.dynamic
                        ? dynamicLabel.length + 'rem'
                        : staticLabel.length + 'rem',
                }"
            />
        </div>
        <div class="characteristic">
            <h5>List used by these nodes</h5>
        </div>
    </div>
</template>

<style scoped>
.characteristic {
    margin: 1rem 1rem 2rem 1rem;
}
.characteristic input {
    text-align: center;
    background: var(--gray-400);
    border-width: 2px;
    height: 3rem;
}
</style>
