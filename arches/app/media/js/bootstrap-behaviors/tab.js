/**
 * Tab behaviour, replacing Bootstrap 3's tab plugin. Moves `.active` between the `<li>`
 * around the trigger and the matching `.tab-pane`, and emits `shown.bs.tab`, which
 * arches listens for to lazily size panels once they become visible.
 */

const TRIGGER_SELECTOR = '[data-toggle="tab"], [data-toggle="pill"]';

function paneFor(trigger) {
    const selector =
        trigger.getAttribute('data-target') || trigger.getAttribute('href') || '';
    if (!selector || selector === '#') {
        return null;
    }
    try {
        return document.querySelector(selector);
    } catch {
        return null;
    }
}

export function show(trigger) {
    const pane = paneFor(trigger);
    const listItem = trigger.closest('li') || trigger;
    const tabList = listItem.closest('ul, nav, .nav');

    if (tabList) {
        for (const sibling of tabList.querySelectorAll('li')) {
            sibling.classList.remove('active');
        }
        for (const other of tabList.querySelectorAll(TRIGGER_SELECTOR)) {
            other.setAttribute('aria-selected', 'false');
        }
    }
    listItem.classList.add('active');
    trigger.setAttribute('aria-selected', 'true');

    if (!pane) {
        return;
    }
    const paneContainer = pane.closest('.tab-content') || pane.parentElement;
    if (paneContainer) {
        for (const sibling of paneContainer.children) {
            if (sibling.classList.contains('tab-pane')) {
                sibling.classList.remove('active', 'in');
            }
        }
    }
    pane.classList.add('active', 'in');

    trigger.dispatchEvent(
        new CustomEvent('shown.bs.tab', { bubbles: true, detail: { target: pane } }),
    );
}

export function install(root = document) {
    root.addEventListener('click', function (event) {
        const trigger = event.target.closest(TRIGGER_SELECTOR);
        if (!trigger) {
            return;
        }
        event.preventDefault();
        show(trigger);
    });
}
