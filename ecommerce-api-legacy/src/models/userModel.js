function findByEmail(db, email) {
    return new Promise((resolve, reject) => {
        db.get('SELECT id, name, email, pass FROM users WHERE email = ?', [email], (err, row) => {
            if (err) reject(err);
            else resolve(row || null);
        });
    });
}

function findById(db, id) {
    return new Promise((resolve, reject) => {
        db.get('SELECT id, name, email FROM users WHERE id = ?', [id], (err, row) => {
            if (err) reject(err);
            else resolve(row || null);
        });
    });
}

function insert(db, name, email, hashedPass) {
    return new Promise((resolve, reject) => {
        db.run(
            'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
            [name, email, hashedPass],
            function(err) {
                if (err) reject(err);
                else resolve(this.lastID);
            }
        );
    });
}

function remove(db, id) {
    return new Promise((resolve, reject) => {
        db.run('DELETE FROM users WHERE id = ?', [id], (err) => {
            if (err) reject(err);
            else resolve();
        });
    });
}

module.exports = { findByEmail, findById, insert, remove };
