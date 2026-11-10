// Regenerates the Protomaps style layers that local basemaps use. Run it from
// a folder where @protomaps/basemaps is installed, so arches itself doesn't
// depend on that package:
//
//   cd "$(mktemp -d)" && npm init -y && npm install @protomaps/basemaps@5.7.2
//   node <arches>/arches/db/local_basemap_styles/generate_style_layers.mjs
//
// Update PROTOMAPS_BASEMAPS_VERSION when upgrading. Styles 5.x read the v4
// tile schema of the Protomaps daily builds.
import { writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath } from "node:url";

const PROTOMAPS_BASEMAPS_VERSION = "5.7.2";
const FLAVORS = ["light", "dark"];
const LANGUAGE = "en";
const SOURCE_NAME = "protomaps";

const requireFromWorkingDirectory = createRequire(path.join(process.cwd(), "package.json"));
const installedVersion = requireFromWorkingDirectory("@protomaps/basemaps/package.json").version;
if (installedVersion !== PROTOMAPS_BASEMAPS_VERSION) {
    throw new Error(`Expected @protomaps/basemaps ${PROTOMAPS_BASEMAPS_VERSION}, found ${installedVersion}`);
}
const { layers, namedFlavor } = requireFromWorkingDirectory("@protomaps/basemaps");

const outputDirectory = path.dirname(fileURLToPath(import.meta.url));
for (const flavor of FLAVORS) {
    const styleLayers = {
        protomaps_basemaps_version: PROTOMAPS_BASEMAPS_VERSION,
        flavor,
        language: LANGUAGE,
        source_name: SOURCE_NAME,
        layers: layers(SOURCE_NAME, namedFlavor(flavor), { lang: LANGUAGE }),
    };
    writeFileSync(path.join(outputDirectory, `${flavor}.json`), JSON.stringify(styleLayers));
    console.log(`${flavor}.json: ${styleLayers.layers.length} layers`);
}
