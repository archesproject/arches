import { defineStore } from "pinia";

import { generateArchesURL } from "@/arches_vue_components/application/generate-arches-url.ts";

interface Settings {
    force_script_name: string;
}

async function requestSettings(): Promise<Settings> {
    const response = await fetch(
        generateArchesURL("arches_vue_components:api-settings"),
    );
    const parsed = await response.json();
    if (!response.ok) {
        throw new Error(parsed.message ?? response.statusText);
    }
    return parsed;
}

export const useSettingsStore = defineStore(
    "arches_vue_components:settings",
    () => {
        let cache: Promise<Settings> | null = null;

        function fetchSettings(): Promise<Settings> {
            if (!cache) {
                cache = requestSettings();
                cache.catch(() => {
                    cache = null;
                });
            }
            return cache;
        }

        async function fetchForceScriptName(): Promise<string> {
            const settings = await fetchSettings();
            return settings.force_script_name;
        }

        return { fetchSettings, fetchForceScriptName };
    },
);
