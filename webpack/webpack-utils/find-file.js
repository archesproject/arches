const fs = require('fs');
const Path = require('path');

function findFile(path, target, excludedDirectories) {
    if (!excludedDirectories) {
        excludedDirectories = [];
    }

    for (const name of fs.readdirSync(path)) {
        const filePath = Path.join(path, name);
        const stat = fs.lstatSync(filePath);

        if (stat.isDirectory() && !excludedDirectories.includes(name)) {
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
