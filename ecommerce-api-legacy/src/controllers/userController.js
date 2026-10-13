const userModel = require('../models/userModel');

async function deleteUser(db, id) {
    const user = await userModel.findById(db, id);
    if (!user) {
        const err = new Error('User not found');
        err.status = 404;
        throw err;
    }
    await userModel.remove(db, id);
    return { deleted: id };
}

module.exports = { deleteUser };
