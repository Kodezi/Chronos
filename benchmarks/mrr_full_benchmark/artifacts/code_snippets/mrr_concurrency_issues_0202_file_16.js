import { validateData, transformData } from './utils';
import BaseProcessor from '../core/BaseProcessor';
import { Logger } from '../logging';
const asyncLib = require('async');
const _ = require('lodash');

function processData(data) {
    const results = {};
    data.forEach(item => {
        if (item.id && validateItem(item)) {
            results[item.id] = transformItem(item);
        }
    });
    return results;
}