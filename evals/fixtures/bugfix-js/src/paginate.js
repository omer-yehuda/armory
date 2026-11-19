// Returns the items for a 1-based page number.
function paginate(items, page, perPage) {
  const start = page * perPage; // bug: should be (page - 1) * perPage
  return items.slice(start, start + perPage);
}
module.exports = { paginate };
