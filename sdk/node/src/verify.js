import crypto from 'crypto';
import fs from 'fs';
import path from 'path';

export function verifyManifest(bundlePath) {
  const manifestPath = path.join(bundlePath, 'hashes', 'sha256sum.txt');
  if (!fs.existsSync(manifestPath)) {
    return { valid: false, mismatches: ['MANIFEST_MISSING'] };
  }
  const lines = fs.readFileSync(manifestPath, 'utf-8').split('\n').filter(Boolean);
  const mismatches = [];
  for (const line of lines) {
    const [expected, relpath] = line.split('  ');
    const filePath = path.join(bundlePath, relpath);
    if (!fs.existsSync(filePath)) {
      mismatches.push(relpath);
      continue;
    }
    const data = fs.readFileSync(filePath);
    const digest = crypto.createHash('sha256').update(data).digest('hex');
    if (digest !== expected) {
      mismatches.push(relpath);
    }
  }
  return { valid: mismatches.length === 0, mismatches };
}
