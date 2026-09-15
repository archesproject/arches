
module.exports = {
    input: {
      path: "./arches", // only files in this directory are considered for extraction
      // Core plus the applications bundled under arches/extensions. They extract
      // into arches/locale rather than per-application catalogs, so one release
      // ships one set of translations.
      include: [
          "app/src/**/*.vue",
          "app/src/**/*.ts",
          "extensions/*/src/**/*.vue",
          "extensions/*/src/**/*.ts",
      ], // glob patterns to select files for extraction

      exclude: [], // glob patterns to exclude files from extraction
      jsExtractorOpts:[ // custom extractor keyword. default empty.
          {
            keyword: "__", // only extractor default keyword such as $gettext,use keyword to custom
            options: {    // see https://github.com/lukasgeiter/gettext-extractor
              content: {
                replaceNewLines: "\n",
              },
              arguments: {
                text: 0,
              },
            },
          },
          {
            keyword: "_n", // $ngettext
            options: {
              content: {
                replaceNewLines: "\n",
              },
              arguments: {
                text: 0,
                textPlural: 1,
              },
            },
          },
        ],
        compileTemplate: false, // do not compile <template> tag when its lang is not html
      },
      output: {
        path: "./arches/locale", // output path of all created files
        potPath: "./messages.pot", // relative to output.path, so by default "./src/language/messages.pot"
        jsonPath: "./", // relative to output.path, so by default "./src/language/translations.json"
        locales: ["en"],
        flat: false, // don't create subdirectories for locales
        linguas: false, // create a LINGUAS file
        splitJson: true, // create separate json files for each locale. If used, jsonPath must end with a directory, not a file
      },
};