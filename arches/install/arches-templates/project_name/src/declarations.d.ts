// import declarations from other projects or Arches core
import("../../node_modules/arches/arches/app/src/declarations.d.ts");

declare module 'arches';
declare module 'arches/*';
declare module 'arches/**';

// declare untyped modules that have been added to your project in `package.json`
// Module homepage on npmjs.com uses logos "TS" or "DT" to indicate if typed

// declare filetypes used in `./src/` folder
declare module "*.ts";
declare module "*.vue";
