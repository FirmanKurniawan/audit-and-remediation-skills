const sqlite3 = require('sqlite3');
module.exports = new sqlite3.Database(process.env.DB_PATH || ':memory:');
