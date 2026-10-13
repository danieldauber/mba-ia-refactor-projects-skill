const express = require('express');
const { getDb } = require('../database');
const checkoutController = require('../controllers/checkoutController');

const router = express.Router();

router.post('/', async (req, res, next) => {
    try {
        const { usr: name, eml: email, pwd: password, c_id: courseId, card: cardNumber } = req.body;
        const result = await checkoutController.processCheckout(getDb(), { name, email, password, courseId, cardNumber });
        res.status(200).json({ msg: 'Success', enrollment_id: result.enrollmentId });
    } catch (err) {
        next(err);
    }
});

module.exports = router;
