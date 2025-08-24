module.exports = {
  apps: [
    {
      name: 'claspp',
      script: 'index.js',
      cwd: '/var/www/claspp_frontend',
      node_args: '--experimental-modules',
      env: { NODE_ENV: 'production', PORT: 8091, HOST: '127.0.0.1' }
    }
  ]
}