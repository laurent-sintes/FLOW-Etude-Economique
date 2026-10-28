import fs from 'node:fs/promises';

const banner = '![Logo eXalt](assets/exalt-logo.png)\n\n**Laurent Sintès** · 19 octobre 2026\n\n---\n\n';
const entries = await fs.readdir('.', {withFileTypes:true});
for (const entry of entries) {
  if (!entry.isFile() || !entry.name.endsWith('.md')) continue;
  const original = await fs.readFile(entry.name, 'utf8');
  if (original.startsWith('![Logo eXalt]')) continue;
  await fs.writeFile(entry.name, banner + original, 'utf8');
  console.log(`BRANDED ${entry.name}`);
}
