/* eslint-disable */

const fs = require('fs');
const os = require('os');
const Path = require('path');
const { compile } = require('@vue/compiler-dom');

const { markCoreComponents } = require('./mark-core-components');

const coreDirectory = fs.mkdtempSync(Path.join(os.tmpdir(), 'mark-core-components-'));
const coreFile = Path.join(fs.realpathSync(coreDirectory), 'Component.vue');

function render(template, filename = coreFile) {
    return compile(template, { filename, nodeTransforms: [markCoreComponents(coreDirectory)] }).code;
}

afterAll(() => {
    fs.rmSync(coreDirectory, { recursive: true, force: true });
});

describe('mark-core-components', () => {
    it('marks the root element of core components only', () => {
        expect(render('<div class="a"><span /></div>')).toContain('"data-arches-core": ""');
        expect(render('<div class="a"><span /></div>').match(/data-arches-core/g)).toHaveLength(1);
        expect(render('<div class="a" />', Path.join(os.tmpdir(), 'Other.vue'))).not.toContain('data-arches-core');
    });

    it('marks every root of a fragment, each v-if branch and roots wrapped in template', () => {
        expect(render('<div v-if="a" /><p v-else /><template v-if="b"><section /></template>').match(/data-arches-core/g)).toHaveLength(3);
    });

    it('skips teleports and slots at the root', () => {
        expect(render('<Teleport to="body"><div /></Teleport><slot />')).not.toContain('data-arches-core');
    });
});
