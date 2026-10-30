/* eslint-disable */

const fs = require('fs');
const Path = require('path');

// Vue template transform: adds data-arches-core to the root element(s) of every component
// compiled from coreDirectory, the boundary the legacy stylesheet fence stops at.

const NODE_ROOT = 0;
const NODE_ELEMENT = 1;
const NODE_ATTRIBUTE = 6;
const WRAPPERS = new Set(['template', 'transition', 'Transition', 'keep-alive', 'KeepAlive', 'suspense', 'Suspense']);
const SKIPPED = new Set(['slot', 'teleport', 'Teleport']);

function markRoots(children) {
    for (const child of children) {
        if (child.type !== NODE_ELEMENT || SKIPPED.has(child.tag)) {
            continue;
        }
        if (WRAPPERS.has(child.tag)) {
            markRoots(child.children);
            continue;
        }
        child.props.push({ type: NODE_ATTRIBUTE, name: 'data-arches-core', value: undefined, loc: child.loc, nameLoc: child.loc });
    }
}

function markCoreComponents(coreDirectory) {
    const directory = fs.realpathSync(coreDirectory) + Path.sep;
    return (node, context) => {
        if (node.type === NODE_ROOT && context.filename?.startsWith(directory)) {
            markRoots(node.children);
        }
    };
}

module.exports = { markCoreComponents };
