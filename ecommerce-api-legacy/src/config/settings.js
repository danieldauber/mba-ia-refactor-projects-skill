const REQUIRED = ['JWT_SECRET'];
const missing = REQUIRED.filter((k) => !process.env[k]);
if (missing.length > 0) {
    console.error(`[FATAL] Missing required environment variables: ${missing.join(', ')}`);
    console.error('Set them before starting the server. Example:');
    missing.forEach((k) => console.error(`  export ${k}=<value>`));
    process.exit(1);
}

const settings = {
    port: parseInt(process.env.PORT, 10) || 3000,
    dbPath: process.env.DB_PATH || ':memory:',
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
    smtpUser: process.env.SMTP_USER || '',
    jwtSecret: process.env.JWT_SECRET,
    bcryptRounds: parseInt(process.env.BCRYPT_ROUNDS, 10) || 12,
};

module.exports = settings;
