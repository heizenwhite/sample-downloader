/** @type {import('next').NextConfig} */
const nextConfig = {
  // skip webpack’s persistent build cache so .next/cache stays small
  experimental: {
    webpackBuildCache: false,
  },
  // if you’re still skipping lint errors in CI:
  eslint: {
    ignoreDuringBuilds: true,
  },
};

module.exports = nextConfig;
