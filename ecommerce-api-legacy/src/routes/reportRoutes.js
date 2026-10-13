const express = require('express');
const { getDb } = require('../database');
const reportController = require('../controllers/reportController');
const { requireAuth } = require('../middlewares/auth');

const router = express.Router();

router.get('/financial-report', requireAuth, async (req, res, next) => {
    try {
        const report = await reportController.getFinancialReport(getDb());
        res.status(200).json(report);
    } catch (err) {
        next(err);
    }
});

module.exports = router;
