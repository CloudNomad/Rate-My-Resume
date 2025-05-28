const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

const sizes = {
  icon: 1024,
  splash: 2048,
  adaptive: 1024,
  favicon: 48
};

async function generateAssets() {
  // Create a simple gradient background
  const gradient = sharp({
    create: {
      width: sizes.icon,
      height: sizes.icon,
      channels: 4,
      background: { r: 0, g: 122, b: 255, alpha: 1 }
    }
  });

  // Generate icon
  await gradient
    .composite([{
      input: Buffer.from(
        `<svg width="${sizes.icon}" height="${sizes.icon}"><text x="50%" y="50%" text-anchor="middle" dy=".3em" fill="white" font-size="200">RMR</text></svg>`
      ),
      gravity: 'center'
    }])
    .toFile(path.join(__dirname, 'icon.png'));

  // Generate splash screen
  await gradient
    .resize(sizes.splash, sizes.splash)
    .composite([{
      input: Buffer.from(
        `<svg width="${sizes.splash}" height="${sizes.splash}"><text x="50%" y="50%" text-anchor="middle" dy=".3em" fill="white" font-size="400">RateMyResume</text></svg>`
      ),
      gravity: 'center'
    }])
    .toFile(path.join(__dirname, 'splash.png'));

  // Generate adaptive icon
  await gradient
    .composite([{
      input: Buffer.from(
        `<svg width="${sizes.adaptive}" height="${sizes.adaptive}"><text x="50%" y="50%" text-anchor="middle" dy=".3em" fill="white" font-size="200">RMR</text></svg>`
      ),
      gravity: 'center'
    }])
    .toFile(path.join(__dirname, 'adaptive-icon.png'));

  // Generate favicon
  await gradient
    .resize(sizes.favicon, sizes.favicon)
    .composite([{
      input: Buffer.from(
        `<svg width="${sizes.favicon}" height="${sizes.favicon}"><text x="50%" y="50%" text-anchor="middle" dy=".3em" fill="white" font-size="24">R</text></svg>`
      ),
      gravity: 'center'
    }])
    .toFile(path.join(__dirname, 'favicon.png'));
}

generateAssets().catch(console.error); 