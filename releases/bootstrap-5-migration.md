# Bootstrap 5 Migration Guide for Arches Extensions

Arches 8.2 upgrades from Bootstrap 3.4.1 to Bootstrap 5.3.6. A CSS compatibility shim is included so most BS3 class names continue to work, but extensions should migrate to native BS5 classes and data attributes.

## Breaking Changes

### 1. Data Attributes Renamed

All Bootstrap data attributes now use a `data-bs-` prefix:

| Bootstrap 3 | Bootstrap 5 |
|---|---|
| `data-toggle="modal"` | `data-bs-toggle="modal"` |
| `data-toggle="collapse"` | `data-bs-toggle="collapse"` |
| `data-toggle="dropdown"` | `data-bs-toggle="dropdown"` |
| `data-toggle="tab"` | `data-bs-toggle="tab"` |
| `data-toggle="tooltip"` | `data-bs-toggle="tooltip"` |
| `data-dismiss="modal"` | `data-bs-dismiss="modal"` |
| `data-dismiss="alert"` | `data-bs-dismiss="alert"` |
| `data-target="#id"` | `data-bs-target="#id"` |
| `data-slide="prev"` | `data-bs-slide="prev"` |
| `data-slide-to="0"` | `data-bs-slide-to="0"` |
| `data-parent="#id"` | `data-bs-parent="#id"` |
| `data-ride="carousel"` | `data-bs-ride="carousel"` |

**Codemod:** Run this from your extension's root to rename all standard data attributes in `.htm` templates:

```bash
find . -name '*.htm' -not -path '*/node_modules/*' -exec sed -i '' \
  -e 's/data-toggle=/data-bs-toggle=/g' \
  -e 's/data-dismiss=/data-bs-dismiss=/g' \
  -e 's/data-target=/data-bs-target=/g' \
  -e 's/data-slide=/data-bs-slide=/g' \
  -e 's/data-slide-to=/data-bs-slide-to=/g' \
  -e 's/data-parent=/data-bs-parent=/g' \
  -e 's/data-ride=/data-bs-ride=/g' {} +
```

> **Important:** If your extension uses custom `data-toggle` or `data-target` attributes that are NOT consumed by Bootstrap (e.g., RDM-specific selectors), do NOT rename those. Check that the value is a standard Bootstrap value (`modal`, `collapse`, `dropdown`, `tab`, `tooltip`, `popover`) before renaming.

### 2. Removed Dependencies

The following npm packages have been removed from arches core and are no longer available:

| Removed Package | Replacement |
|---|---|
| `knockstrap` | Custom KO bindings (see `arches/app/media/js/bindings/carousel.js`) |
| `bootstrap-colorpicker` | Native `<input type="color">` via KO binding (see `arches/app/media/js/bindings/color-picker.js`) |

If your extension imports either of these, remove the import and switch to the new bindings.

### 3. jQuery Plugin Bridge

Arches provides a jQuery-to-BS5 compatibility bridge at `arches/app/media/js/utils/bootstrap-jquery-compat.js`. The following jQuery calls continue to work:

- `$(el).modal('show' | 'hide' | 'toggle')`
- `$(el).tooltip(options | 'show' | 'hide' | 'destroy')`
- `$(el).dropdown('toggle' | 'show' | 'hide')`
- `$(el).collapse('show' | 'hide' | 'toggle')`
- `$(el).tab('show')`
- `$(el).carousel(options)`

If your JS code uses these jQuery patterns, they will continue to work. However, new code should use the native BS5 API:

```javascript
import * as bootstrap from 'bootstrap';
bootstrap.Modal.getOrCreateInstance(element).show();
bootstrap.Tooltip.getOrCreateInstance(element).show();
```

### 4. `nodeModulesPaths` Changes

If your extension's `package.json` has a `nodeModulesPaths` section, update these entries:

```json
// REMOVE these entries if present:
"knockstrap": "...",
"bootstrap-colorpicker": "...",

// UPDATE bootstrap alias:
"bootstrap": "plugins/../js/utils/bootstrap-jquery-compat",
"bootstrap-bundle": "plugins/../../../../node_modules/bootstrap/dist/js/bootstrap.bundle.min",
```

## CSS Class Changes (Compatibility Shim)

Arches includes `bootstrap3-compat.css` which maps common BS3 classes to BS5 equivalents. These BS3 classes will continue to render correctly, but extensions should migrate to native BS5 classes over time:

| Bootstrap 3 | Bootstrap 5 |
|---|---|
| `.panel` | `.card` |
| `.panel-heading` | `.card-header` |
| `.panel-body` | `.card-body` |
| `.panel-footer` | `.card-footer` |
| `.panel-title` | `.card-title` |
| `.panel-default` | `.card` (no variant needed) |
| `.well` | `.bg-light .border .rounded .p-3` |
| `.btn-default` | `.btn-secondary` |
| `.col-xs-*` | `.col-*` |
| `.pull-left` | `.float-start` |
| `.pull-right` | `.float-end` |
| `.hidden-xs` | `.d-none .d-sm-block` |
| `.hidden-sm` | `.d-sm-none .d-md-block` |
| `.hidden-md` | `.d-md-none .d-lg-block` |
| `.hidden-lg` | `.d-lg-none` |
| `.visible-xs` | `.d-block .d-sm-none` |
| `.visible-sm` | `.d-none .d-sm-block .d-md-none` |
| `.visible-md` | `.d-none .d-md-block .d-lg-none` |
| `.visible-lg` | `.d-none .d-lg-block` |
| `.img-responsive` | `.img-fluid` |
| `.input-lg` | `.form-control-lg` |
| `.input-sm` | `.form-control-sm` |
| `.form-group` | `.mb-3` |
| `.control-label` | `.form-label` |
| `.help-block` | `.form-text` |
| `.input-group-addon` | `.input-group-text` |
| `.page-header` | heading with `.pb-2 .border-bottom` |

### Glyphicons

Bootstrap 5 does not include Glyphicons. Arches uses Font Awesome 4 (`font-awesome@4.6.3`). Replace any `glyphicon` references:

| Glyphicon | Font Awesome |
|---|---|
| `glyphicon glyphicon-search` | `fa fa-search` |
| `glyphicon glyphicon-plus` | `fa fa-plus` |
| `glyphicon glyphicon-remove` | `fa fa-times` |
| `glyphicon glyphicon-ok` | `fa fa-check` |
| `glyphicon glyphicon-chevron-right` | `fa fa-chevron-right` |
| `glyphicon glyphicon-pencil` | `fa fa-pencil` |
| `glyphicon glyphicon-trash` | `fa fa-trash` |

## Extension Impact Summary

Based on audit of downstream extensions:

| Extension | Total Hits | Primary Issues |
|---|---|---|
| arches-her | 54 | `col-xs-` (45), `data-toggle` (4), `data-dismiss` (1) |
| arches-rascolls | 20 | `col-xs-` (12), `data-toggle` (5), `.panel` (2) |
| arches-search | 9 | `.panel` (7), `data-toggle` (1) |
| arches-controlled-lists | 6 | `col-xs-` (4), `data-toggle` (1) |
| arches-lingo | 3 | `data-toggle` (1), `.panel` (1) |
| arches-component-lab | 2 | `data-toggle` (1) — index.htm navbar only |
| arches-modular-reports | 2 | `.panel` (2) |
| arches-querysets | 0 | Clean |
| arches-ai-agent | 0 | Clean |
| arches-addressing | 0 | Clean (own source) |

## Migration Checklist

For each extension:

- [ ] Run the `data-*` codemod on `.htm` templates
- [ ] Verify `data-toggle`/`data-target` usages are standard Bootstrap (not custom selectors)
- [ ] Remove `knockstrap` and `bootstrap-colorpicker` from `package.json` dependencies and `nodeModulesPaths`
- [ ] Update `bootstrap` entry in `nodeModulesPaths` to use the compat bridge
- [ ] Add `bootstrap-bundle` entry to `nodeModulesPaths`
- [ ] Update `bootstrap` dependency to `"5.3.6"`
- [ ] Add `"@popperjs/core": "2.11.8"` to dependencies
- [ ] Replace any `glyphicon` classes with Font Awesome equivalents
- [ ] Test all modals, dropdowns, tooltips, tabs, and collapse components
- [ ] Plan incremental migration of `.panel` and `col-xs-` classes to native BS5
