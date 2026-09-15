import ko from 'knockout';

/**
 * Colour picker binding, replacing bootstrap-colorpicker 2.5.3.
 *
 * That package is Bootstrap 3-only — it renders its popup with `.dropdown-menu`
 * and positions against BS3's box model — and has been unmaintained since 2019.
 *
 * bootstrap-colorpicker left the bound element as a text input showing the colour
 * string and opened a popup when the adjacent swatch was clicked, so both typing a
 * value and picking one worked. This keeps both.
 *
 * All eleven call sites already wrap the input in an `.input-group` ending with an
 * `.input-group-addon` holding an `ion-stop` icon tinted to the current colour. So
 * rather than adding a visible control — which would land inside the input-group and
 * break its layout — a native `<input type="color">` is overlaid transparently on
 * that existing addon. The swatch looks exactly as it did and now opens the platform
 * colour picker, which is what clicking it used to do. Where no addon is present the
 * swatch is appended to the group instead.
 *
 * `type="color"` cannot express an alpha channel, so `format: 'rgba'` also gets an
 * opacity slider.
 *
 * Usage is unchanged:
 *     data-bind="colorPicker: {color: someObservable, format: 'rgba'}"
 *
 * The `container` option bootstrap-colorpicker used to position its popup is
 * accepted and ignored — an overlaid native swatch needs no positioning.
 */

const SWATCH_CLASS = 'color-picker-swatch';
const ALPHA_CLASS = 'color-picker-alpha';

function hexToRgb(hex) {
    let normalized = hex.replace(/^#/, '');
    if (normalized.length === 3) {
        normalized = normalized[0] + normalized[0]
            + normalized[1] + normalized[1]
            + normalized[2] + normalized[2];
    }
    const value = parseInt(normalized, 16);
    return { red: (value >> 16) & 255, green: (value >> 8) & 255, blue: value & 255 };
}

function rgbToHex(red, green, blue) {
    return '#' + ((1 << 24) + (red << 16) + (green << 8) + blue).toString(16).slice(1);
}

/** Accepts the hex and rgb/rgba spellings bootstrap-colorpicker emitted. */
function parseColor(rawValue) {
    const value = String(rawValue ?? '').trim();

    const rgbMatch = value.match(
        /^rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+)\s*)?\)$/
    );
    if (rgbMatch) {
        return {
            hex: rgbToHex(Number(rgbMatch[1]), Number(rgbMatch[2]), Number(rgbMatch[3])),
            alpha: rgbMatch[4] === undefined ? 1 : parseFloat(rgbMatch[4]),
        };
    }

    if (/^#[0-9a-f]{3}$/i.test(value) || /^#[0-9a-f]{6}$/i.test(value)) {
        return { hex: value.length === 4 ? expandShorthandHex(value) : value, alpha: 1 };
    }

    // Eight-digit hex carries alpha in the last pair.
    if (/^#[0-9a-f]{8}$/i.test(value)) {
        return { hex: value.slice(0, 7), alpha: parseInt(value.slice(7), 16) / 255 };
    }

    return null;
}

function expandShorthandHex(hex) {
    return '#' + hex[1] + hex[1] + hex[2] + hex[2] + hex[3] + hex[3];
}

function formatColor(hex, alpha, format) {
    if (format !== 'rgba') {
        return hex;
    }
    const { red, green, blue } = hexToRgb(hex);
    return `rgba(${red}, ${green}, ${blue}, ${alpha})`;
}

ko.bindingHandlers.colorPicker = {
    init: function (element, valueAccessor) {
        const options = ko.unwrap(valueAccessor());
        const colorObservable = options.color;
        const format = options.format || 'hex';

        const initialColor = parseColor(ko.unwrap(colorObservable)) || { hex: '#000000', alpha: 1 };

        // Guards the two-way sync: writing to the observable re-enters this
        // binding through its own subscription.
        let synchronizing = false;

        const swatch = document.createElement('input');
        swatch.type = 'color';
        swatch.value = initialColor.hex;
        swatch.setAttribute('aria-label', element.getAttribute('placeholder') || 'Select a color');

        // Prefer the addon already in the markup: overlaying it keeps the control
        // looking untouched and makes the existing swatch open the picker.
        const inputGroup = element.closest('.input-group');
        const existingAddon = inputGroup && inputGroup.querySelector('.input-group-addon');

        if (existingAddon) {
            swatch.className = `${SWATCH_CLASS} ${SWATCH_CLASS}--overlay`;
            existingAddon.classList.add(`${SWATCH_CLASS}-host`);
            existingAddon.appendChild(swatch);
        } else {
            swatch.className = SWATCH_CLASS;
            element.parentNode.insertBefore(swatch, element.nextSibling);
        }

        let alphaSlider = null;
        if (format === 'rgba') {
            alphaSlider = document.createElement('input');
            alphaSlider.type = 'range';
            alphaSlider.className = ALPHA_CLASS;
            alphaSlider.min = '0';
            alphaSlider.max = '1';
            alphaSlider.step = '0.01';
            alphaSlider.value = String(initialColor.alpha);
            alphaSlider.setAttribute('aria-label', 'Opacity');
            // Outside the input-group, so the group's own layout is untouched.
            (inputGroup || element).insertAdjacentElement('afterend', alphaSlider);
        }

        if (!element.value) {
            element.value = formatColor(initialColor.hex, initialColor.alpha, format);
        }

        function writeToObservable(hex, alpha) {
            if (!ko.isObservable(colorObservable)) {
                return;
            }
            synchronizing = true;
            colorObservable(formatColor(hex, alpha, format));
            synchronizing = false;
        }

        function currentAlpha() {
            return alphaSlider ? parseFloat(alphaSlider.value) : 1;
        }

        swatch.addEventListener('input', function () {
            const alpha = currentAlpha();
            element.value = formatColor(swatch.value, alpha, format);
            writeToObservable(swatch.value, alpha);
        });

        if (alphaSlider) {
            alphaSlider.addEventListener('input', function () {
                const alpha = currentAlpha();
                element.value = formatColor(swatch.value, alpha, format);
                writeToObservable(swatch.value, alpha);
            });
        }

        // A value typed into the text input only propagates once it parses, so
        // a half-typed "#ab" does not clobber the observable.
        element.addEventListener('input', function () {
            const parsed = parseColor(element.value);
            if (!parsed) {
                return;
            }
            swatch.value = parsed.hex;
            if (alphaSlider) {
                alphaSlider.value = String(parsed.alpha);
            }
            writeToObservable(parsed.hex, parsed.alpha);
        });

        if (ko.isObservable(colorObservable)) {
            const subscription = colorObservable.subscribe(function (newValue) {
                if (synchronizing) {
                    return;
                }
                const parsed = parseColor(newValue);
                if (!parsed) {
                    return;
                }
                element.value = formatColor(parsed.hex, parsed.alpha, format);
                swatch.value = parsed.hex;
                if (alphaSlider) {
                    alphaSlider.value = String(parsed.alpha);
                }
            });

            ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
                subscription.dispose();
            });
        }
    }
};

ko.bindingHandlers.colorPicker.init = ko.bindingHandlers.colorPicker.init.bind(ko.bindingHandlers.colorPicker);
export default ko.bindingHandlers.colorPicker;
