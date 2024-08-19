import ControlledListsMain from "@/arches_references/components/ControlledListsMain.vue";

export const routes = [
    {
        path: "/plugins/controlled-list-manager",
        name: "splash",
        component: ControlledListsMain,
    },
    {
        path: "/plugins/controlled-list-manager/list/:id",
        name: "list",
        component: ControlledListsMain,
    },
    {
        path: "/plugins/controlled-list-manager/item/:id",
        name: "item",
        component: ControlledListsMain,
    },
];

export const routeNames = {
    splash: "splash",
    list: "list",
    item: "item",
};
