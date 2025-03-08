module.exports = {
    transform: {
        '^.+\\.jsx?$': 'babel-jest',
    },
    testEnvironment: 'jsdom',
    silent: process.env.JEST_SILENT === 'true',
};