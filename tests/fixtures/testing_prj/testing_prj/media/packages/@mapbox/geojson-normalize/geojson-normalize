#!/usr/bin/env node

var normalize = require('./'),
    fs = require('fs');


process.stdout.write(JSON.stringify(normalize(JSON.parse(fs.readFileSync(process.argv[2])))));
