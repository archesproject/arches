<script setup>
import { ref, onMounted, watch } from "vue";
import Button from "primevue/button";
import Dropdown from "primevue/dropdown";
import InputText from "primevue/inputtext";
import uuid from "uuid";
import arches from "arches";
import Cookies from "js-cookie";

const props = defineProps(["etlModuleId"]);

const graphid = ref();
const selectedGraph = ref();
const fileName = ref();
const exportConceptsAs = ref("uuids");
const formData = new FormData();
const loadid = uuid.generate();
const moduleId = props.etlModuleId;

const graphs = arches.resources.map((resource) => ({
    name: resource.name,
    graphid: resource.graphid,
}));

const exportResources = async () => {
    formData.append("graph_id", selectedGraph.value);
    formData.append("graph_name", getGraphName(selectedGraph.value));
    formData.append("export_concepts_as", exportConceptsAs.value);
    const response = await submit("export");
    // activeTab("import");

    if (response.ok) {
        const json = await response.json();
        console.log(json.result);
    } else {
        const err = await response.json();
        console.log(err);
        // self.alert(
        //     new JsonErrorAlertViewModel(
        //         "ep-alert-red",
        //         err.data,
        //         null,
        //         function () {}
        //     )
        // );
    }
};

const getGraphName = (selectedGraphId) => {
    if (graphs) {
        return graphs.find((graph) => graph.graphid === selectedGraphId).name;
    }
};

const submit = (action) => {
    formData.append("action", action);
    formData.append("load_id", loadid);
    formData.append("module", moduleId);

    if (fileName) {
        formData.append("filename", fileName.value);
    }

    return fetch(arches.urls.etl_manager, {
        method: "POST",
        body: formData,
        credentials: "include",
        headers: {
            "X-CSRFToken": Cookies.get("csrftoken"),
        },
    });
};
</script>

<template>
    <div class="etl-module-component-container">
        <div class="etl-module-body">
            <h2>
                <span Export Branch Excel></span>
            </h2>
            <section class="etl-module-component">
                <div class="etl-module-component-block">
                    <h3>
                        <label>Select a Resource Model</label>
                    </h3>
                    <Dropdown
                        v-model="selectedGraph"
                        :options="graphs"
                        optionLabel="name"
                        optionValue="graphid"
                        placeholder="Select a Resource Model"
                        class="w-full md:w-14rem target-model-dropdown"
                    />
                </div>
                <div style="padding-top: 16px">
                    <h3>
                        <label
                            >Choose a name for the exported file
                            (optional)</label
                        >
                    </h3>
                    <InputText class="file-name-input" v-model="fileName" />
                </div>
                <div
                    v-if="selectedGraph"
                    @click="exportResources"
                    style="margin-top: 40px"
                >
                    <Button label="Submit" />
                </div>
            </section>
        </div>
    </div>
</template>
<style>
.etl-module-component-container {
    display: flex;
    flex-wrap: wrap;
    flex-direction: column;
    align-content: flex-start;
    align-items: flex-start;
    height: 100vh;
}
.file-name-input {
    border: 1px solid #ddd;
    padding: 4px;
    border-radius: 2px;
    width: 500px;
    height: 30px;
}
</style>
