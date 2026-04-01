import { spawnSync } from 'node:child_process';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const jestBin = require.resolve('jest/bin/jest');

const forwardedArgs = process.argv.slice(2);
const normalizedArgs =
  forwardedArgs[0] === '--' ? forwardedArgs.slice(1) : forwardedArgs;

const result = spawnSync(
  process.execPath,
  [jestBin, '--config=jest.e2e.config.js', ...normalizedArgs],
  {
    stdio: 'inherit',
    env: process.env,
  },
);

if (result.error) {
  throw result.error;
}

process.exit(result.status ?? 1);
