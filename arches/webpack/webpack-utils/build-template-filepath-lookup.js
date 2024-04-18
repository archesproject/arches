const Path = require('path');
const fs = require('fs');

const buildTemplateFilePathLookup = function(path, outerAcc, templateDirectoryPath) {
    if (!fs.existsSync(path)) {
        return;
    }
    
    return fs.readdirSync(path).reduce((acc, name) => {
        const outerPath = templateDirectoryPath || path;   // original `path` arg is persisted through recursion
        
        if (fs.lstatSync(Path.join(path, name)).isDirectory() ) {
            return buildTemplateFilePathLookup(
                Path.join(path, name), 
                acc, 
                outerPath
            );
        }
        else {
            const regex = new RegExp(`${Path.sep}templates${Path.sep}(.*)`, 's');
            const subPath = Path.join(path, name).split(regex)[1];  // splits only on first occurrence

            const parsedPath = Path.parse(subPath);
            const filename = parsedPath['dir'] ? Path.join(parsedPath['dir'], parsedPath['base']) : parsedPath['base'];

            if (filename.includes('.DS_Store')) {
                return acc;
            }
            else {
                return { 
                    ...acc, 
                    [Path.join('templates', filename).replace(/\\/g, '/')]: Path.resolve(__dirname, Path.join(outerPath, subPath))
                };
            }
        }
    }, outerAcc);
};

module.exports = { buildTemplateFilePathLookup };