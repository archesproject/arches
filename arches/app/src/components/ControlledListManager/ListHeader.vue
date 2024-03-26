<script setup lang="ts">
import { computed, inject } from "vue";
import { useGettext } from "vue3-gettext";

const { $gettext } = useGettext();
const slateBlue = "#2d3c4b"; // todo: import from theme somewhere

const { displayedList } = inject("displayedList");

const heading = computed(() => {
    if (!displayedList) {
        return $gettext("List Editor");
    }
    return $gettext(
        "List Editor > %{listName}",
        { listName: displayedList.value.name },
    );
});
</script>

<template>
    <div
        class="header"
        :style="{ background: slateBlue }"
    >
        <i
            class="fa fa-inverse fa-list"
            aria-hidden="true"
        />
        <h2>{{ heading }}</h2>
    </div>
</template>

<style scoped>
.header {
    display: flex;
    align-items: center;
}
i {
    margin-left: 1rem;
    margin-top: 0.25rem;
}
h2 {
    font-size: 1.5rem;
    margin: 1rem;
    color: white;
}
</style>
