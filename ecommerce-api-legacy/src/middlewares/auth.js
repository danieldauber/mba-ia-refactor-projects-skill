const settings = require('../config/settings');

function requireAuth(req, res, next) {
    const token = req.headers['x-api-key'];
    if (!token || token !== settings.jwtSecret) {
        return res.status(401).json({ error: 'Unauthorized' });
    }
    next();
}

module.exports = { requireAuth };
