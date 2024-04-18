const Path = require('path');
const fs = require('fs');

const buildImageFilePathLookup = function(publicPath, path, outerAcc, imageDirectoryPath) {
    if (!fs.existsSync(path)) {
        return;
    }

    return fs.readdirSync(path).reduce((acc, name) => {
        const outerPath = imageDirectoryPath || path;   // original `path` arg is persisted through recursion
        
        if (fs.lstatSync(Path.join(path, name)).isDirectory() ) {
            return buildImageFilePathLookup(
                publicPath,
                Path.join(path, name), 
                acc, 
                outerPath
            );
        }
        else {
            const regex = new RegExp(`${Path.sep}img${Path.sep}(.*)`, 's');
            const subPath = Path.join(path, name).split(regex)[1];  // splits only on first occurrence

            const parsedPath = Path.parse(subPath);
            const filename = parsedPath['dir'] ? Path.join(parsedPath['dir'], parsedPath['base']) : parsedPath['base'];

            return { 
                ...acc, 
                [Path.join(publicPath, 'img', filename).replace(/\\/g, '/')]: Path.resolve(__dirname, Path.join(outerPath, subPath))
            };
        }
    }, outerAcc);
};

module.exports = { buildImageFilePathLookup };