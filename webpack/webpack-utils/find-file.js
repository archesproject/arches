const fs = require('fs');
const Path = require('path');

function findFile(path, target) {
    for (const name of fs.readdirSync(path)) {
        const filePath = Path.join(path, name);
        const stat = fs.lstatSync(filePath);

        if (stat.isDirectory() && name !== 'node_modules') {
            const result = findFile(filePath, target);
            if (result) {
                return result;
            }
        } else if (name === target) {
            return filePath;
        }
    }
}

module.exports = { findFile };
