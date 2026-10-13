const settings = {
    port: parseInt(process.env.PORT, 10) || 3000,
    dbPath: process.env.DB_PATH || ':memory:',
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
    smtpUser: process.env.SMTP_USER || '',
    jwtSecret: process.env.JWT_SECRET || 'change-me-in-production',
    bcryptRounds: parseInt(process.env.BCRYPT_ROUNDS, 10) || 12,
};

module.exports = settings;
