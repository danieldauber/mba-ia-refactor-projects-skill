const sqlite3 = require('sqlite3').verbose();
const settings = require('./config/settings');

let _db = null;

function getDb() {
    if (!_db) {
        _db = new sqlite3.Database(settings.dbPath);
        _db.run('PRAGMA foreign_keys = ON');
    }
    return _db;
}

function seed(db) {
    return new Promise((resolve, reject) => {
        db.serialize(() => {
            db.run(`CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                pass TEXT NOT NULL
            )`);
            db.run(`CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                price REAL NOT NULL,
                active INTEGER NOT NULL DEFAULT 1
            )`);
            db.run(`CREATE TABLE IF NOT EXISTS enrollments (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                course_id INTEGER NOT NULL REFERENCES courses(id)
            )`);
            db.run(`CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY,
                enrollment_id INTEGER NOT NULL REFERENCES enrollments(id) ON DELETE CASCADE,
                amount REAL NOT NULL,
                status TEXT NOT NULL
            )`);
            db.run(`CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY,
                action TEXT NOT NULL,
                created_at DATETIME NOT NULL DEFAULT (datetime('now'))
            )`);

            const bcrypt = require('bcryptjs');
            const settings = require('./config/settings');
            const seedPass = bcrypt.hashSync('123', settings.bcryptRounds);

            db.run(
                "INSERT INTO users (name, email, pass) VALUES (?, ?, ?)",
                ['Leonan', 'leonan@fullcycle.com.br', seedPass]
            );
            db.run(
                "INSERT INTO courses (title, price, active) VALUES (?, ?, 1), (?, ?, 1)",
                ['Clean Architecture', 997.00, 'Docker', 497.00]
            );
            db.run(
                "INSERT INTO enrollments (user_id, course_id) VALUES (1, 1)"
            );
            db.run(
                "INSERT INTO payments (enrollment_id, amount, status) VALUES (1, 997.00, 'PAID')",
                [],
                (err) => { if (err) reject(err); else resolve(); }
            );
        });
    });
}

module.exports = { getDb, seed };
