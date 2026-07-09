import { defineStore } from "pinia";
import { ref } from "vue";

import { fetchLanguages } from "@/arches_component_lab/widgets/api.ts";

import type { Language } from "@/arches_component_lab/types.ts";

export const useLanguageStore = defineStore(
    "arches_component_lab:language",
    () => {
        const languages = ref<Language[]>([]);
        let fetchPromise: Promise<Language[]> | null = null;

        function fetchAllLanguages(): Promise<Language[]> {
            if (!fetchPromise) {
                fetchPromise = fetchLanguages()
                    .then((response: { languages: Language[] }) => {
                        languages.value = response.languages;
                        return response.languages;
                    })
                    .catch((error: unknown) => {
                        fetchPromise = null;
                        throw error;
                    });
            }
            return fetchPromise;
        }

        return { languages, fetchAllLanguages };
    },
);
