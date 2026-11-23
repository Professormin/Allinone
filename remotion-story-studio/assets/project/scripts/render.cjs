const fs = require('node:fs');
const path = require('node:path');
const {spawnSync} = require('node:child_process');
const [composition, output, ...extra] = process.argv.slice(2);
if (!composition || !output) throw new Error('Usage: node scripts/render.cjs COMPOSITION OUTPUT [Remotion options]');
const temp = path.resolve('work/temp');
fs.mkdirSync(temp, {recursive:true});
const cli = path.join(path.dirname(require.resolve('@remotion/cli/package.json')), 'remotion-cli.js');
const result = spawnSync(process.execPath,[cli,'render','src/index.ts',composition,output,...extra],{
 stdio:'inherit', env:{...process.env,TMP:temp,TEMP:temp,TMPDIR:temp}
});
if (result.error) throw result.error;
process.exit(result.status ?? 1);
