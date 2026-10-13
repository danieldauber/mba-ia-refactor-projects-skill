function insert(db, action) {
    return new Promise((resolve, reject) => {
        db.run(
            "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
            [action],
            (err) => {
                if (err) reject(err);
                else resolve();
            }
        );
    });
}

module.exports = { insert };
