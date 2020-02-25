/// <reference types="geojson" />

import {Points} from '@turf/helpers';

declare function gridToMatrix(points: Points, property?: string): Array<Array<number>>;
declare namespace gridToMatrix { }
export = gridToMatrix;
