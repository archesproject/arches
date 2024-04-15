const Path = require('path');
const fs = require('fs');

function buildCSSFilepathLookup(path, outerAcc, cssDirectoryPath) {
    if (!fs.existsSync(path)) {
        return;
    }
    
    return fs.readdirSync(path).reduce((acc, name) => {
        const outerPath = cssDirectoryPath || path;   // original `path` arg is persisted through recursion
        
        if (fs.lstatSync(Path.join(path, name)).isDirectory() ) {
            return buildCSSFilepathLookup(
                Path.join(path, name), 
                acc, 
                outerPath 
            );
        }
        else {
            let subPath = Path.join(path, name).split(/css(.*)/s)[1];  // splits only on first occurance
            subPath = subPath.substring(1);
            const parsedPath = Path.parse(subPath);

            let pathName = parsedPath['name'];
        
            if (parsedPath['dir']) {
                pathName = Path.join(parsedPath['dir'], parsedPath['name']);
            }

            if (pathName.includes('.DS_Store')) {
                return acc;
            }
            else {
                return { 
                    ...acc, 
                    [Path.join('css', pathName.replace(/\\/g, '/'))]: { 'import': Path.join(outerPath, subPath) } 
                };
            }
        }
    }, outerAcc);
};

module.exports = { buildCSSFilepathLookup };
