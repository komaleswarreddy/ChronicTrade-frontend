/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Turbopack configuration (Next.js 16+ uses Turbopack by default)
  // Empty config to silence the warning - Turbopack handles caching better
  turbopack: {},
}

module.exports = nextConfig

