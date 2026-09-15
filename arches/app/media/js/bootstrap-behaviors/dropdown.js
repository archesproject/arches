/**
 * Dropdown behaviour, replacing Bootstrap 3's dropdown plugin.
 *
 * Drives the same markup the plugin did — a trigger carrying
 * `data-toggle="dropdown"` inside a `.dropdown` (or `.btn-group`), with a sibling
 * `.dropdown-menu` — by toggling `.open` on the parent, which is what the vendored
 * Bootstrap 3 stylesheet already styles. Twelve triggers across the templates.
 */

const TRIGGER_SELECTOR = '[data-toggle="dropdown"]';
const PARENT_SELECTOR = '.dropdown, .btn-group, .dropup, .input-group-btn';
const OPEN_CLASS = 'open';

function parentOf(trigger) {
    return trigger.closest(PARENT_SELECTOR) || trigger.parentElement;
}

function closeAll(except) {
    for (const open of document.querySelectorAll(`.${OPEN_CLASS}`)) {
        if (open === except) {
            continue;
        }
        // Only close things that are actually dropdowns; `.open` is a generic enough
        // class name that arches uses it elsewhere.
        if (!open.querySelector(TRIGGER_SELECTOR)) {
            continue;
        }
        open.classList.remove(OPEN_CLASS);
        const trigger = open.querySelector(TRIGGER_SELECTOR);
        if (trigger) {
            trigger.setAttribute('aria-expanded', 'false');
        }
    }
}

export function toggle(trigger) {
    const parent = parentOf(trigger);
    if (!parent) {
        return;
    }
    const willOpen = !parent.classList.contains(OPEN_CLASS);
    closeAll(willOpen ? parent : null);
    parent.classList.toggle(OPEN_CLASS, willOpen);
    trigger.setAttribute('aria-expanded', String(willOpen));
}

export function hideAll() {
    closeAll(null);
}

export function install(root = document) {
    root.addEventListener('click', function (event) {
        const trigger = event.target.closest(TRIGGER_SELECTOR);
        if (trigger) {
            event.preventDefault();
            toggle(trigger);
            return;
        }
        // A click inside an open menu should not close it; anywhere else should.
        if (!event.target.closest('.dropdown-menu')) {
            closeAll(null);
        }
    });

    root.addEventListener('keydown', function (event) {
        if (event.key === 'Escape') {
            closeAll(null);
        }
    });
}
