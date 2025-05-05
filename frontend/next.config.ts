/** @type {import('next').NextConfig} */
const nextConfig = {
  // skip webpack’s persistent build cache so .next/cache stays small
  output: 'export',
  experimental: {
    webpackBuildCache: false,
  },
  // if you’re still skipping lint errors in CI:
  eslint: {
    ignoreDuringBuilds: true,
  },
};
export default nextConfig
module.exports = nextConfig;
