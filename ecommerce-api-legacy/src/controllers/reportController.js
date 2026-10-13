const courseModel = require('../models/courseModel');

async function getFinancialReport(db) {
    const rows = await courseModel.findAllWithRevenueData(db);

    const courses = {};
    for (const row of rows) {
        if (!courses[row.course_id]) {
            courses[row.course_id] = { course: row.title, revenue: 0, students: [] };
        }
        if (row.enrollment_id) {
            if (row.status === 'PAID') {
                courses[row.course_id].revenue += row.amount;
            }
            courses[row.course_id].students.push({
                student: row.student_name || 'Unknown',
                paid: row.amount || 0,
            });
        }
    }

    return Object.values(courses);
}

module.exports = { getFinancialReport };
