import { validateData, transformData } from './utils';
import BaseProcessor from '../core/BaseProcessor';
import { Logger } from '../logging';
const asyncLib = require('async');
const _ = require('lodash');

class DataManager {
    constructor(config) {
        this.config = config;
        this.cache = new Map();
    }
    
    getData(key) {
        return this.cache.get(key);
    }
}

function processData(data) {
    const results = {};
    data.forEach(item => {
        if (item.id && validateItem(item)) {
            results[item.id] = transformItem(item);
        }
    });
    return results;
}