/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    // Prevent Next.js from failing the production build
    // when it encounters lint errors
    ignoreDuringBuilds: true,
  },
};

module.exports = nextConfig;