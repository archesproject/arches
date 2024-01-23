<script setup>
import { computed, ref } from "vue";
import Column from "primevue/column";
import DataTable from "primevue/datatable";

const slateBlue = "#2d3c4b"; // todo: import from theme somewhere
const { displayedList } = defineProps(["displayedList"]);

const heading = computed(() => {
    return (
        "List Editor" +
        (displayedList.value ? " > " + displayedList.value.name : "")
    );
});

const rowClass = (rowData) => {
    const depth = `depth-${rowData.depth}`;
    if (rowData.children.length) {
        return depth;
    }
    return `${depth} no-expander`;
};

const selectedLanguage = "en";

const expandedRows = ref([]);
const onRowExpand = (row) => {
    expandedRows.value.push(row.data.id);
};
const onRowCollapse = (row) => {
    expandedRows.value.splice(expandedRows.value.indexOf(row.data.id));
};
const onRowReorder = (dragData) => {
    // todo: hit server
};

const itemsForLanguage = computed(() => {
    // Show/hide rows based on row expansion toggle
    const itemsToShow = displayedList.value.items.reduce((acc, row) => {
        if (!row.parent_id) {
            acc.push(row);
        } else if (expandedRows.value.includes(row.parent_id)) {
            acc.push(row);
        }
        return acc;
    }, []);

    // Flatten labels
    return itemsToShow.map((item) => {
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

    <div v-if="!!displayedList.value" class="list-editor-container">
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

        <div class="items">
            <h4 style="margin-top: 4rem; margin-left: 0">
                Items ({{ displayedList.value.items.length }})
            </h4>
            <!-- TODO: language selector -->
            <!-- TreeTable exists, but DataTable has better support for reordering -->
            <DataTable
                :value="itemsForLanguage"
                :rowClass="rowClass"
                stripedRows
                scrollable
                scrollHeight="400px"
                tableStyle="font-size: 14px; table-layout: fixed"
                :pt="{
                    bodyRow: { style: { height: '4rem' } },
                }"
                @rowExpand="onRowExpand"
                @rowCollapse="onRowCollapse"
                @rowReorder="onRowReorder"
            >
                <Column
                    expander
                    style="width: 3rem"
                    :pt="{
                        headerCell: { style: { borderTop: 0 } },
                        headerContent: { style: { height: '4rem' } },
                    }"
                />
                <Column
                    rowReorder
                    style="width: 3rem"
                    :pt="{
                        headerCell: { style: { borderTop: 0 } },
                    }"
                />
                <Column
                    field="prefLabels"
                    header="Item Labels"
                    sortable
                    :pt="{
                        headerCell: { style: { borderTop: 0, width: '220px' } },
                    }"
                />
                <Column
                    field="altLabels"
                    header="Alternate Labels"
                    sortable
                    :pt="{
                        headerCell: { style: { borderTop: 0, width: '220px' } },
                    }"
                />
                <Column
                    field="uri"
                    header="Item URI"
                    sortable
                    :pt="{
                        headerCell: { style: { borderTop: 0 } },
                    }"
                />
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
    margin-top: 0.25rem;
}
h4 {
    margin: 1rem;
    color: white;
}
.characteristic {
    margin: 1rem 1rem 2rem 1rem;
}
.characteristic input {
    text-align: center;
    background: var(--gray-400);
    border-width: 2px;
    height: 3rem;
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

<style>
/* https://github.com/primefaces/primevue/issues/1834#issuecomment-982831184 */
.p-datatable .p-datatable-tbody > tr.no-expander > td .p-row-toggler {
    display: none;
}
.depth-1 > td:nth-child(2),
.depth-1 > td:nth-child(3) {
    padding-left: 2rem;
}
.depth-2 > td:nth-child(2),
.depth-2 > td:nth-child(3) {
    padding-left: 4rem;
}
.depth-3 > td:nth-child(2),
.depth-3 > td:nth-child(3) {
    padding-left: 6rem;
}
.depth-4 > td:nth-child(2),
.depth-4 > td:nth-child(3) {
    padding-left: 8rem;
}
</style>
