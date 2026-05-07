import $ from 'jquery';
import ko from 'knockout';

function hexToRgb(hex) {
    hex = hex.replace(/^#/, '');
    if (hex.length === 3) {
        hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
    }
    var num = parseInt(hex, 16);
    return { r: (num >> 16) & 255, g: (num >> 8) & 255, b: num & 255 };
}

function rgbToHex(r, g, b) {
    return '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
}

function parseColor(str) {
    str = (str || '').trim();
    var match = str.match(/^rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+)\s*)?\)$/);
    if (match) {
        return {
            hex: rgbToHex(+match[1], +match[2], +match[3]),
            alpha: match[4] !== undefined ? parseFloat(match[4]) : 1
        };
    }
    if (/^#[0-9a-f]{3,8}$/i.test(str)) {
        return { hex: str.length > 7 ? str.slice(0, 7) : str, alpha: 1 };
    }
    return { hex: '#000000', alpha: 1 };
}

function toRgbaString(hex, alpha) {
    var rgb = hexToRgb(hex);
    return 'rgba(' + rgb.r + ', ' + rgb.g + ', ' + rgb.b + ', ' + alpha + ')';
}

ko.bindingHandlers.colorPicker = {
    init: function (element, valueAccessor) {
        var options = ko.unwrap(valueAccessor());
        var colorObs = options.color;
        var format = options.format || 'hex';
        var updating = false;

        element.type = 'color';
        element.style.cursor = 'pointer';

        var parsed = parseColor(ko.unwrap(colorObs));
        element.value = parsed.hex;

        var alphaInput = null;
        if (format === 'rgba') {
            alphaInput = document.createElement('input');
            alphaInput.type = 'range';
            alphaInput.min = '0';
            alphaInput.max = '1';
            alphaInput.step = '0.01';
            alphaInput.value = String(parsed.alpha);
            alphaInput.title = 'Opacity';
            alphaInput.style.width = '100%';
            alphaInput.style.marginTop = '4px';
            element.parentNode.insertBefore(alphaInput, element.nextSibling);
        }

        function emitValue() {
            if (updating) { return; }
            updating = true;
            var hex = element.value;
            if (format === 'rgba') {
                var alpha = alphaInput ? parseFloat(alphaInput.value) : 1;
                colorObs(toRgbaString(hex, alpha));
            } else {
                colorObs(hex);
            }
            updating = false;
        }

        element.addEventListener('input', emitValue);
        if (alphaInput) {
            alphaInput.addEventListener('input', emitValue);
        }

        if (ko.isObservable(colorObs)) {
            colorObs.subscribe(function (val) {
                if (updating) { return; }
                updating = true;
                var p = parseColor(val);
                element.value = p.hex;
                if (alphaInput) {
                    alphaInput.value = String(p.alpha);
                }
                updating = false;
            });
        }
    }
};

ko.bindingHandlers.colorPicker.init = ko.bindingHandlers.colorPicker.init.bind(ko.bindingHandlers.colorPicker);
export default ko.bindingHandlers.colorPicker;
