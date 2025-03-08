const isProduction = process.env.NODE_ENV === 'production';

const config = {
    // Use relative URLs in production so browser requests go to the same origin
    // and Nginx can proxy them to the backend service
    apiBaseUrl: isProduction ? '/api' : 'http://localhost:9090/api',
    webSocketUrl: isProduction ? '/ws' : 'ws://localhost:9090/ws',
};
export default config;