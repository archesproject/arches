<script setup>
import { computed } from "vue";
import DataTable from "primevue/datatable";
import Column from "primevue/column";

const slateBlue = "#2d3c4b"; // todo: import from theme somewhere
const { selectedList } = defineProps(["selectedList"]);

const heading = computed(() => {
    return (
        "List Editor" +
        (selectedList.value ? " > " + selectedList.value.name : "")
    );
});

const selectedLanguage = "en";
const itemsForLanguage = computed(() => {
    if (!selectedList.value) {
        return {};
    }
    // todo: do something with children
    return selectedList.value.items.map((item) => {
        return {
            ...item,
            prefLabels: [
                ...item.labels
                    .filter(
                        (label) =>
                            label.language === selectedLanguage &&
                            label.valuetype === "prefLabel"
                    )
                    .map((label) => label.value),
            ].join(", "),
            altLabels: [
                ...item.labels
                    .filter(
                        (label) =>
                            label.language === selectedLanguage &&
                            label.valuetype === "altLabel"
                    )
                    .map((label) => label.value),
            ].join(", "),
        };
    });
});

const staticLabel = "Static: list does not change";
const dynamicLabel =
    "Dynamic: list is defined by a query that may change list items";
</script>

<template>
    <div class="header" :style="{ background: slateBlue }">
        <i class="fa fa-inverse fa-list" aria-hidden="true"></i>
        <h4>{{ heading }}</h4>
    </div>

    <div v-if="!!selectedList.value" class="list-editor-container">
        <div class="characteristics">
            <h4>Characteristics</h4>
            <div class="characteristic">
                <h5>Name</h5>
                <span>{{ selectedList.value.name }}</span>
            </div>
            <div class="characteristic">
                <h5>Type</h5>
                <span>
                    {{
                        selectedList.value.dynamic ? dynamicLabel : staticLabel
                    }}</span
                >
            </div>
            <div class="characteristic">
                <h5>List used by these nodes</h5>
            </div>
        </div>

        <div class="items">
            <h4 style="margin-top: 4rem; margin-left: 0">Items</h4>
            <!-- TODO: language selector -->
            <DataTable
                :value="itemsForLanguage"
                stripedRows
                scrollable
                scrollHeight="400px"
                tableStyle="font-size: 14px; table-layout: fixed"
                :pt="{
                    bodyRow: { style: { height: '4rem' } },
                }"
            >
                <Column
                    field="prefLabels"
                    header="Item Labels"
                    sortable
                    :pt="{
                        headerCell: { style: { borderTop: 0, width: '250px' } },
                        headerContent: { style: { height: '4rem' } },
                    }"
                ></Column>
                <Column
                    field="altLabels"
                    header="Alternate Labels"
                    sortable
                    :pt="{
                        headerCell: { style: { borderTop: 0, width: '250px' } },
                        headerContent: { style: { height: '4rem' } },
                    }"
                ></Column>
                <Column
                    field="uri"
                    header="Item URI"
                    sortable
                    :pt="{
                        headerCell: { style: { borderTop: 0 } },
                        headerContent: { style: { height: '4rem' } },
                    }"
                ></Column>
            </DataTable>
        </div>
    </div>

    <div v-else id="rr-splash" class="rr-splash">
        <!-- Image -->
        <div
            aria-hidden="true"
            class="img-lg img-circle rr-splash-img-container"
        >
            <i class="fa fa-list"></i>
        </div>

        <!-- Splash Title -->
        <div class="rr-splash-title">
            Welcome to Arches' Controlled List Manager
        </div>

        <!-- Splash Instructions -->
        <div class="rr-splash-description">Select a list from the sidebar.</div>
    </div>
</template>

<style scoped>
.header {
    display: flex;
    align-items: center;
}
i {
    margin-left: 1rem;
    margin-top: 0.5rem;
}
h4 {
    margin: 1rem;
    color: white;
}
.characteristic {
    margin: 1rem 1rem 2rem 1rem;
}
.list-editor-container {
    margin: 1rem;
}
.items,
table {
    margin: inherit;
}
.list-editor-container h4 {
    color: gray;
    border-bottom: 1px solid lightgray;
    font-weight: 400;
}
</style>
