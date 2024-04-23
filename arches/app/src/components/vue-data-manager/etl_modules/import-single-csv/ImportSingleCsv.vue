<script setup>
import Card from "primevue/card";
import Button from "primevue/button";
import Dropdown from "primevue/dropdown";
import FileUpload from "primevue/fileupload";
import InputSwitch from "primevue/inputswitch";
import { ref, onMounted, watch, computed } from "vue";
import uuid from "uuid";
import arches from "arches";
import Cookies from "js-cookie";

const action = "read";
const loadid = uuid.generate();
const formData = new FormData();
const languages = arches.languages;
const moduleid = "0a0cea7e-b59a-431a-93d8-e9f8c41bdd6b";

const nodes = ref();
const csvBody = ref();
const headers = ref();
const csvArray = ref();
const numOfCols = ref();
const numOfRows = ref();
const csvExample = ref();
const csvFileName = ref();
const selectedResourceModel = ref();
const fileInfo = ref({});
const stringNodes = ref([]);
const fieldMapping = ref([]);
const columnHeaders = ref([]);
const allResourceModels = ref([]);
const fileAdded = ref(false);
const hasHeaders = ref(true);

const ready = computed(() => {
    return selectedResourceModel.value && fieldMapping.value.find((v) => v.node);
});

const prepRequest = (ev) => {
    ev.formData.append("action", action);
    ev.formData.append("load_id", loadid);
    ev.formData.append("module", moduleid);
    ev.xhr.withCredentials = true;
    ev.xhr.setRequestHeader("X-CSRFToken", Cookies.get("csrftoken"));
};

async function prefetch() {
    getGraphs();
}

const getGraphs = function () {
    submit("get_graphs").then(function (response) {
        allResourceModels.value = response.result;
    });
};

const submit = function (action) {
    formData.append("action", action);
    formData.append("load_id", loadid);
    formData.append("module", moduleid);
    return $.ajax({
        type: "POST",
        url: arches.urls.etl_manager,
        data: formData,
        cache: false,
        processData: false,
        contentType: false,
    });
};

watch(csvArray, async (val) => {
    numOfRows.value = val.length;
    numOfCols.value = val[0].length;
    if (hasHeaders.value) {
        columnHeaders.value = val[0];
        csvBody.value = val.slice(1);
    } else {
        columnHeaders.value = null;
        csvBody.value = val;
    }
});

watch(selectedResourceModel, async (graph) => {
    if (graph) {
        formData.append("graphid", graph);
        submit("get_nodes").then(function (response) {
            const theseNodes = response.result.map((node) => ({
                ...node,
                label: node.alias,
            }));
            stringNodes.value = theseNodes.reduce((acc, node) => {
                if (node.datatype === "string") {
                    acc.push(node.alias);
                }
                return acc;
            }, []);
            theseNodes.unshift({
                alias: "resourceid",
                label: arches.translations.idColumnSelection,
            });
            nodes.value = theseNodes;
        });
    }
});

watch(columnHeaders, async (headers) => {
    if (headers) {
        fieldMapping.value = headers.map(function (header) {
            return {
                field: header,
                node: ref(),
                language: ref(
                    arches.languages.find(
                        (lang) => lang.code == arches.activeLanguage
                    )
                ),
            };
        });
    }
});

watch(hasHeaders, async (val) => {
    headers.value = null;
    if (val) {
        headers.value = csvArray.value[0];
        csvBody.value = csvArray.value.slice(1);
    } else {
        headers.value = Array.apply(0, Array(csvArray.value[0].length)).map(
            function (_, b) {
                return b + 1;
            }
        );
        csvBody.value = csvArray.value;
    }
});

watch(selectedResourceModel, async (graph) => {
    if (!graph) {
        nodes.value = null;
    }
});

watch(csvBody, async (val) => {
    numOfRows.value = val.length;
    csvExample.value = val.slice(0, 5);
});

const formatSize = function (size) {
    var bytes = size;
    if (bytes == 0) return "0 Byte";
    var k = 1024;
    var dm = 2;
    var sizes = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"];
    var i = Math.floor(Math.log(bytes) / Math.log(k));
    return (
        "<strong>" +
        parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) +
        "</strong> " +
        sizes[i]
    );
};

const addFile = function (file) {
    fileInfo.value = { name: file.name, size: file.size };
    formData.append("file", file, file.name);
    submit("read")
        .then(function (response) {
            csvArray.value = response.result.csv;
            csvFileName.value = response.result.csv_file;
            if (response.result.config) {
                fieldMapping.value = response.result.config.mapping;
                selectedResourceModel.value = response.result.config.graph;
            }
            formData.delete("file");
            fileAdded.value = true;
        })
        .fail(function (err) {
            console.log(err);
        });
};
const write = function () {
    if (!ready.value) {
        return;
    }
    const fieldnames = fieldMapping.value.map((fieldname) => {
        return fieldname.node;
    });
    formData.append("fieldnames", fieldnames);
    formData.append("fieldMapping", JSON.stringify(fieldMapping));
    formData.append("hasHeaders", hasHeaders.value);
    formData.append("graphid", selectedResourceModel.value);
    formData.append("csvFileName", csvFileName.value);
    // loading(true);
    submit("start")
        .then((data) => {
            // activeTab.value = 2;
            formData.append("async", true);
            submit("write")
                .then((data) => {
                    console.log(data.result);
                })
                .fail(function (err) {
                    console.log(err);
                });
        })
        .fail((error) => console.log(error));

    console.log(fieldnames);
};

onMounted(async () => {
    await prefetch();
});
</script>

<template>
    <div class="import-single-csv-container">
        <div class="import-single-csv-component-container">
            <div class="card flex justify-content-center">
                <FileUpload
                    v-if="!fileAdded"
                    mode="basic"
                    name="file"
                    choose-label="Browse"
                    :url="arches.urls.root"
                    :max-file-size="1000000"
                    :auto="true"
                    :multiple="true"
                    @upload="addFile($event.files[0])"
                    @before-send="prepRequest($event)"
                />
            </div>
        </div>

        <div class="import-single-csv-component-container">
            <Card 
                v-if="fileAdded" 
                style="box-shadow: none"
            >
                <div class="title-text">
                    <h4>File Summary</h4>
                </div>
                <div>
                    <div>
                        <span class="etl-loading-metadata-key">File Name:</span>
                        <span class="etl-loading-metadata-value">{{
                            fileInfo.name
                        }}</span>
                    </div>
                    <div>
                        <span class="etl-loading-metadata-key">File Size:</span>
                        <span class="etl-loading-metadata-value">{{
                            fileInfo.size
                        }}</span>
                    </div>
                    <div>
                        <span class="etl-loading-metadata-key">
                            Number of Rows:
                        </span>
                        <span class="etl-loading-metadata-value">{{
                            numOfRows
                        }}</span>
                    </div>
                </div>
            </Card>
        </div>

        <div
            v-if="fileAdded"
            class="import-single-csv-component-container"
            style="margin: 20px"
        >
            <h4>Target Model</h4>
            <Dropdown
                v-model="selectedResourceModel"
                :options="allResourceModels"
                option-label="name"
                option-value="graphid"
                placeholder="Select a Resource Model"
                class="w-full md:w-14rem target-model-dropdown"
            />
        </div>
        <div
            v-if="fileAdded && selectedResourceModel"
            class="import-single-csv-component-container"
            style="margin: 20px"
        >
            <h4 style="margin-bottom: 15px">
                Import Details
            </h4>
            <div
                class="card flex justify-content-center"
                style="display: flex; align-items: baseline"
            >
                <InputSwitch v-model="hasHeaders" />
                <p class="content-text">
                    Column names in the first row
                </p>
            </div>
        </div>
        <div
            v-if="fileAdded && selectedResourceModel"
            class="import-single-csv-component-container"
            style="margin: 20px"
        >
            <div class="csv-mapping-table-container">
                <table class="table table-striped csv-mapping-table">
                    <thead>
                        <tr>
                            <th
                                v-for="(mapping, index) in fieldMapping" 
                                v-if="nodes"
                                :key="index"
                                style="
                                    border-bottom: 1px solid #ddd;
                                    vertical-align: top;
                                "
                            >
                                <Dropdown
                                    v-model="mapping.node"
                                    :options="nodes"
                                    option-label="name"
                                    option-value="alias"
                                    placeholder="Select a Node"
                                />
                                <Dropdown
                                    v-if="stringNodes.includes(mapping.node)"
                                    v-model="mapping.language"
                                    :options="languages"
                                    :option-label="
                                        function (item) {
                                            return (
                                                item.name +
                                                ' (' +
                                                item.code +
                                                ')'
                                            );
                                        }
                                    "
                                />
                            </th>
                        </tr>
                    </thead>
                    <thead>
                        <tr class="column-names">
                            <th
                                v-for="(col, index) in columnHeaders" 
                                :key="index"
                                style="border-bottom: 1px solid #ddd"
                            >
                                {{ col }}
                            </th>
                        </tr>
                    </thead>

                    <tbody>
                        <tr 
                            v-for="(row, index) in csvExample" 
                            :key="index"
                        >
                            <td
                                v-for="(cell, child_index) in row"
                                :key="child_index"
                                style="vertical-align: text-top"
                            >
                                {{ cell }}
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        <div 
            v-if="ready"
            class="import-single-csv-component-container" 
        >
            <Button 
                :disabled="!!!ready" 
                label="Submit" 
                @click="write" 
            />
        </div>
    </div>
</template>

<style>
.card .p-button {
    width: 200px;
}

.p-dropdown-items-wrapper {
    max-height: 100% !important;
}

.import-single-csv-container {
    display: flex;
    flex-wrap: wrap;
    flex-direction: column;
    align-content: flex-start;
    align-items: flex-start;
}

.import-single-csv-component-container {
    width: fit-content;
    margin-left: 20px;
}
.title-text {
    font-size: 1.5rem;
    font-weight: 700;
}
.target-model-dropdown {
    width: 500px;
}
.content-text {
    font-size: 1.5rem;
    font-weight: 100;
    margin-left: 20px;
}
</style>
