const logger = require('./logger');

function errorHandler(err, req, res, next) {
    logger.error({ err: err.message, stack: err.stack, path: req.path });
    const status = err.status || 500;
    res.status(status).json({ error: err.message || 'Internal server error' });
}

module.exports = { errorHandler };
