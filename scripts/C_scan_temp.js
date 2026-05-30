// Script C — Scan de pastas temp-like (read-only, sem efeitos)
// Data de criação: 2026-05-10
// Data de execução: 2026-05-10
// Status: EXECUTADO (read-only)
// Output esperado: lista de candidatas com nome, path, n_items, n_subs, earliest e latest dateAdded
//
// Heurística: pastas cujo nome contém "temp", "untitled", data YYYY-MM-DD, ou lixo conhecido
//
// Resultado real: 26 candidates encontradas (vide NEWS.md)

const lib = Zotero.Libraries.userLibraryID;
const allColls = Zotero.Collections.getByLibrary(lib, true);

function isTempCandidate(name) {
  const n = name.trim();
  if (/^untitled/i.test(n)) return true;
  if (/temp/i.test(n)) return true;
  if (/\d{4}-\d{2}-\d{2}/.test(n)) return true;
  if (/^(etaetaeta|fwef|sub \d+|dd)$/i.test(n)) return true;
  return false;
}

function fullPath(c) {
  const parts = [c.name];
  let p = c.parentID;
  while (p) {
    const par = Zotero.Collections.get(p);
    if (!par) break;
    parts.unshift(par.name);
    p = par.parentID;
  }
  return parts.join(' / ');
}

const candidates = allColls.filter(c => isTempCandidate(c.name));
const out = [];

for (const c of candidates) {
  const items = c.getChildItems();
  let earliest = null, latest = null;
  for (const it of items) {
    const d = it.dateAdded;
    if (d) {
      if (!earliest || d < earliest) earliest = d;
      if (!latest || d > latest) latest = d;
    }
  }
  const subs = c.getChildCollections();
  out.push({
    name: c.name,
    path: fullPath(c),
    nItems: items.length,
    nSubs: subs.length,
    earliest: earliest ? earliest.substring(0, 10) : '',
    latest: latest ? latest.substring(0, 10) : '',
    subNames: subs.map(s => s.name).join(' | ')
  });
}

out.sort((a, b) => (a.earliest || 'zzzz-zz-zz').localeCompare(b.earliest || 'zzzz-zz-zz'));

let txt = `=== ${out.length} temp-like candidates ===\n\n`;
for (const r of out) {
  txt += `[${r.earliest || '????-??-??'} → ${r.latest || '????-??-??'}] ${r.name}\n`;
  txt += `  Path: ${r.path}\n`;
  txt += `  Direct items: ${r.nItems} | Subs: ${r.nSubs}`;
  if (r.subNames) txt += ` (${r.subNames})`;
  txt += '\n\n';
}
return txt;
