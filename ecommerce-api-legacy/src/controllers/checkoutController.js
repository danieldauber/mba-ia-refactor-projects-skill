const bcrypt = require('bcryptjs');
const settings = require('../config/settings');
const userModel = require('../models/userModel');
const courseModel = require('../models/courseModel');
const enrollmentModel = require('../models/enrollmentModel');
const paymentModel = require('../models/paymentModel');
const auditService = require('../services/auditService');

const VISA_PREFIX = '4';

async function processCheckout(db, { name, email, password, courseId, cardNumber }) {
    if (!name || !email || !courseId || !cardNumber) {
        const err = new Error('Missing required fields: name, email, courseId, cardNumber');
        err.status = 400;
        throw err;
    }

    const course = await courseModel.findById(db, courseId);
    if (!course) {
        const err = new Error('Course not found or inactive');
        err.status = 404;
        throw err;
    }

    const paymentStatus = cardNumber.startsWith(VISA_PREFIX) ? 'PAID' : 'DENIED';
    if (paymentStatus === 'DENIED') {
        const err = new Error('Payment denied');
        err.status = 400;
        throw err;
    }

    let user = await userModel.findByEmail(db, email);
    let userId;
    if (!user) {
        const raw = password || '123456';
        const hashed = await bcrypt.hash(raw, settings.bcryptRounds);
        userId = await userModel.insert(db, name, email, hashed);
    } else {
        userId = user.id;
    }

    const enrollmentId = await enrollmentModel.insert(db, userId, courseId);
    await paymentModel.insert(db, enrollmentId, course.price, paymentStatus);
    await auditService.onCheckout(db, userId, course.title);

    return { enrollmentId, userId, courseTitle: course.title };
}

module.exports = { processCheckout };
