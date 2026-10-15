import arches from "arches";
import ControlledListsMain from "@/arches_controlled_lists/components/ControlledListsMain.vue";

export const routes = [
    {
        path: arches.urls.plugin("controlled-list-manager"),
        name: "splash",
        component: ControlledListsMain,
    },
    {
        path: arches.urls.plugin("controlled-list-manager/list/:id"),
        name: "list",
        component: ControlledListsMain,
    },
    {
        path: arches.urls.plugin("controlled-list-manager/item/:id"),
        name: "item",
        component: ControlledListsMain,
    },
];

export const routeNames = {
    splash: "splash",
    list: "list",
    item: "item",
};
