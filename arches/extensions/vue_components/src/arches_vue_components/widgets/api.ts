import { generateArchesURL } from "@/arches_vue_components/application/generate-arches-url.ts";

export async function fetchLanguages() {
    const response = await fetch(
        generateArchesURL(
            "arches_vue_components:api-languages-with-request-language",
        ),
    );
    const parsed = await response.json();
    if (!response.ok) throw new Error(parsed.message || response.statusText);
    return parsed;
}
