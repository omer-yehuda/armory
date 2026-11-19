const test = require('node:test');
const assert = require('node:assert');
const { paginate } = require('./paginate');
test('first page', () => assert.deepStrictEqual(paginate([1, 2, 3, 4, 5], 1, 2), [1, 2]));
test('last partial page', () => assert.deepStrictEqual(paginate([1, 2, 3, 4, 5], 3, 2), [5]));
test('page past the end', () => assert.deepStrictEqual(paginate([1, 2, 3], 5, 2), []));
