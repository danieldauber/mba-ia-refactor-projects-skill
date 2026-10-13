const express = require('express');
const settings = require('./config/settings');
const { getDb, seed } = require('./database');
const logger = require('./middlewares/logger');
const { errorHandler } = require('./middlewares/errorHandler');

const checkoutRoutes = require('./routes/checkoutRoutes');
const reportRoutes = require('./routes/reportRoutes');
const userRoutes = require('./routes/userRoutes');

const app = express();
app.use(express.json());

app.use('/api/checkout', checkoutRoutes);
app.use('/api/admin', reportRoutes);
app.use('/api/users', userRoutes);

app.use(errorHandler);

seed(getDb())
    .then(() => {
        app.listen(settings.port, () => {
            logger.info({ port: settings.port }, 'Server started');
        });
    })
    .catch((err) => {
        logger.error({ err: err.message }, 'Database seed failed');
        process.exit(1);
    });
