function findById(db, id) {
    return new Promise((resolve, reject) => {
        db.get('SELECT id, title, price, active FROM courses WHERE id = ? AND active = 1', [id], (err, row) => {
            if (err) reject(err);
            else resolve(row || null);
        });
    });
}

function findAllWithRevenueData(db) {
    return new Promise((resolve, reject) => {
        db.all(`
            SELECT
                c.id AS course_id,
                c.title,
                e.id AS enrollment_id,
                u.name AS student_name,
                p.amount,
                p.status
            FROM courses c
            LEFT JOIN enrollments e ON e.course_id = c.id
            LEFT JOIN users u ON u.id = e.user_id
            LEFT JOIN payments p ON p.enrollment_id = e.id
            ORDER BY c.id
        `, [], (err, rows) => {
            if (err) reject(err);
            else resolve(rows);
        });
    });
}

module.exports = { findById, findAllWithRevenueData };
