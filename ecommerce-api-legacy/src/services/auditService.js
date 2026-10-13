const logger = require('../middlewares/logger');
const auditLogModel = require('../models/auditLogModel');

async function onCheckout(db, userId, courseTitle) {
    logger.info(`Checkout: user=${userId} course="${courseTitle}"`);
    await auditLogModel.insert(db, `Checkout course "${courseTitle}" by user ${userId}`);
}

module.exports = { onCheckout };
