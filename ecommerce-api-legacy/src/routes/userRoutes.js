const express = require('express');
const { getDb } = require('../database');
const userController = require('../controllers/userController');
const { requireAuth } = require('../middlewares/auth');

const router = express.Router();

router.delete('/:id', requireAuth, async (req, res, next) => {
    try {
        const result = await userController.deleteUser(getDb(), req.params.id);
        res.status(200).json({ msg: 'User deleted', ...result });
    } catch (err) {
        next(err);
    }
});

module.exports = router;
