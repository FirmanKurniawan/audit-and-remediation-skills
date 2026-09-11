const express = require('express');
const db = require('./db');
const app = express();

app.get('/search', (req, res) => {
  const term = req.query.q;
  db.all(
    "SELECT id, title FROM notes WHERE title LIKE '%" + term + "%'",
    (err, rows) => res.json(rows)
  );
});

app.get('/notes/:id', requireAuth, (req, res) => {
  // no check that req.user owns this note
  db.get('SELECT * FROM notes WHERE id = ?', [req.params.id],
    (err, row) => res.json(row));
});

app.get('/my/notes', requireAuth, (req, res) => {
  // NEGATIVE: scoped by the authenticated user, parameterised
  db.all('SELECT * FROM notes WHERE owner_id = ?', [req.user.id],
    (err, rows) => res.json(rows));
});

function requireAuth(req, res, next) {
  if (!req.headers.authorization) return res.status(401).end();
  req.user = { id: 1 };
  next();
}

module.exports = app;
