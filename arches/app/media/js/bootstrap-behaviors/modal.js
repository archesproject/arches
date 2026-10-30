/**
 * Modal behaviour, replacing Bootstrap 3's modal plugin. The vendored stylesheet still
 * carries `.modal`, `.modal-backdrop` and `.modal-open`, so this drives the same
 * classes.
 *
 * Focus is deliberately not trapped: Bootstrap 3's focus enforcement broke the select2
 * and chosen dropdowns arches renders inside modals, which is why `rdm.js` used to
 * neutralise it by overriding `enforceFocus`.
 */

const BACKDROP_CLASS = 'modal-backdrop';
const TRANSITION_MS = 300;

const openModals = [];

function hasFade(element) {
    return element.classList.contains('fade');
}

function createBackdrop(element) {
    const backdrop = document.createElement('div');
    backdrop.className = hasFade(element)
        ? `${BACKDROP_CLASS} fade`
        : `${BACKDROP_CLASS} in`;
    document.body.appendChild(backdrop);
    if (hasFade(element)) {
        void backdrop.offsetHeight;
        backdrop.classList.add('in');
    }
    return backdrop;
}

export function show(element) {
    if (!element || openModals.some((entry) => entry.element === element)) {
        return;
    }

    const backdrop = createBackdrop(element);
    openModals.push({ element, backdrop });

    document.body.classList.add('modal-open');
    element.style.display = 'block';
    element.removeAttribute('aria-hidden');
    element.setAttribute('aria-modal', 'true');

    void element.offsetHeight;
    element.classList.add('in');

    element.dispatchEvent(new CustomEvent('shown.bs.modal', { bubbles: true }));
}

export function hide(element) {
    const index = openModals.findIndex((entry) => entry.element === element);
    if (index === -1) {
        return;
    }
    const { backdrop } = openModals[index];
    openModals.splice(index, 1);

    element.classList.remove('in');
    backdrop.classList.remove('in');

    const finish = () => {
        element.style.display = 'none';
        element.setAttribute('aria-hidden', 'true');
        element.removeAttribute('aria-modal');
        backdrop.remove();
        if (openModals.length === 0) {
            document.body.classList.remove('modal-open');
        }
        element.dispatchEvent(new CustomEvent('hidden.bs.modal', { bubbles: true }));
    };

    if (hasFade(element)) {
        window.setTimeout(finish, TRANSITION_MS);
    } else {
        finish();
    }
}

export function toggle(element) {
    if (openModals.some((entry) => entry.element === element)) {
        hide(element);
    } else {
        show(element);
    }
}

function topMost() {
    return openModals.length ? openModals[openModals.length - 1].element : null;
}

export function install(root = document) {
    root.addEventListener('click', function (event) {
        const dismiss = event.target.closest('[data-dismiss="modal"]');
        if (dismiss) {
            const element = dismiss.closest('.modal');
            if (element) {
                event.preventDefault();
                hide(element);
            }
            return;
        }

        // Clicking the backdrop closes, matching Bootstrap 3's default.
        const element = topMost();
        if (element && event.target === element) {
            hide(element);
        }
    });

    root.addEventListener('keydown', function (event) {
        if (event.key !== 'Escape') {
            return;
        }
        const element = topMost();
        if (element) {
            hide(element);
        }
    });
}
