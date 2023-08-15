const Path = require('path');
const fs = require('fs');

const buildVueFilePathLookup = function(path, outerAcc, vueDirectoryPath) {
    if (!fs.existsSync(path)) {
        return;
    }
    
    return fs.readdirSync(path).reduce((acc, name) => {
        const outerPath = vueDirectoryPath || path;   // original `path` arg is persisted through recursion
        
        if (fs.lstatSync(Path.join(path, name)).isDirectory() ) {
            return buildVueFilePathLookup(
                Path.join(path, name), 
                acc, 
                outerPath
            );
        }
        else {
            let subPath = (Path.join(path, name)).split(/src(.*)/s)[1];  // splits only on first occurance
            subPath = subPath.substring(1);

            const parsedPath = Path.parse(subPath);
            const filename = parsedPath['dir'] ? Path.join(parsedPath['dir'], parsedPath['base']) : parsedPath['base'];

            if (filename.includes('.DS_Store')) {
                return acc;
            }
            else {
                return { 
                    ...acc, 
                    [filename.replace(/\\/g, '/')]: Path.resolve(__dirname, Path.join(outerPath, subPath))
                };
            }
        }
    }, outerAcc);
};

module.exports = { buildVueFilePathLookup };