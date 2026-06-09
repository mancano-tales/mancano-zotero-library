// Script J — Enriquecer metadados via DOI (CrossRef) / ISBN (OpenLibrary)
// Data de criação: 2026-05-30
// Data de execução: 2026-05-30
// Status: EXECUTADO
// Output esperado: ~28 tentativas (9 via DOI + 19 via ISBN); preencher só campos vazios.
//
// Contexto:
//   Parte da Fase 0.5 (resolver coleção "Problematic - No author" do user).
//   Triagem em python/classify_problematic.py classificou 114 itens em 3 baldes.
//   Este script ataca o Balde A: itens que têm DOI ou ISBN e podem ser
//   enriquecidos via API externa.
//
// O quê:
//   1) Para cada item, lê DOI ou ISBN.
//   2) Chama CrossRef (DOI) ou OpenLibrary (ISBN).
//   3) Preenche APENAS campos vazios (NUNCA sobrescreve via setIfEmpty).
//   4) Atribui creators APENAS se o item não tem nenhum.
//
// Segurança:
//   - setIfEmpty() checa item.getField(name) — se já tem valor, pula.
//   - item.getCreators().length === 0 antes de setCreators().
//   - Rate-limit: 250ms entre itens, 1s a cada 10.
//
// Resultado real (2026-05-30):
//   11 enriquecidos, 0 falhas, 17 sem mudança.
//   - 17 sem mudança = OpenLibrary não tinha dados para ISBNs brasileiros pequenos
//     OU o item já tinha tudo preenchido.
//   - Enriquecidos: 151 (publisher), 1054 (numPages+creators), 5045 (creators),
//     6867/7021/7038/7039 (publicationTitle), 8434 (place+numPages+abstract+creator),
//     9417 (publisher), 11644 (publisher), 11886 (title).

const ITEMS = [{"id": 151, "action": "enrich_via_doi", "lookup_key": "10.1590/S0103-40141997000300011"}, {"id": 705, "action": "enrich_via_isbn", "lookup_key": "978-85-8044-959-4"}, {"id": 822, "action": "enrich_via_isbn", "lookup_key": "978-0-8047-6814-6"}, {"id": 1054, "action": "enrich_via_isbn", "lookup_key": "978-85-273-0111-4"}, {"id": 5045, "action": "enrich_via_isbn", "lookup_key": "978-85-7541-350-0"}, {"id": 6337, "action": "enrich_via_isbn", "lookup_key": "978-85-510-0614-6"}, {"id": 6357, "action": "enrich_via_isbn", "lookup_key": "978-85-441-0302-9"}, {"id": 6368, "action": "enrich_via_isbn", "lookup_key": "978-85-8057-649-8"}, {"id": 6375, "action": "enrich_via_isbn", "lookup_key": "978-85-422-1707-0"}, {"id": 6422, "action": "enrich_via_isbn", "lookup_key": "978-85-7559-321-9"}, {"id": 6425, "action": "enrich_via_isbn", "lookup_key": "978-85-7753-228-5"}, {"id": 6432, "action": "enrich_via_isbn", "lookup_key": "978-85-88808-82-9"}, {"id": 6435, "action": "enrich_via_isbn", "lookup_key": "978-85-5451-185-2"}, {"id": 6439, "action": "enrich_via_isbn", "lookup_key": "978-85-5451-361-0"}, {"id": 6440, "action": "enrich_via_isbn", "lookup_key": "978-85-209-3649-8"}, {"id": 6867, "action": "enrich_via_doi", "lookup_key": "10.1515/9781400829828-008"}, {"id": 7021, "action": "enrich_via_doi", "lookup_key": "10.1016/bs.hefe.2016.10.003"}, {"id": 7038, "action": "enrich_via_doi", "lookup_key": "10.1201/9781003226055-19"}, {"id": 7039, "action": "enrich_via_doi", "lookup_key": "10.1201/9781003226055-10"}, {"id": 7353, "action": "enrich_via_isbn", "lookup_key": "978-1-0353-2777-5"}, {"id": 8434, "action": "enrich_via_isbn", "lookup_key": "978-85-283-0005-5"}, {"id": 8435, "action": "enrich_via_isbn", "lookup_key": "978-85-326-5179-2"}, {"id": 9373, "action": "enrich_via_isbn", "lookup_key": "978-85-8482-360-4"}, {"id": 9400, "action": "enrich_via_isbn", "lookup_key": "978-85-7496-426-3"}, {"id": 9417, "action": "enrich_via_doi", "lookup_key": "10.3982/ECTA8121"}, {"id": 11644, "action": "enrich_via_doi", "lookup_key": "10.1787/343652001507"}, {"id": 11885, "action": "enrich_via_doi", "lookup_key": "10.4337/9781035371341"}, {"id": 11886, "action": "enrich_via_doi", "lookup_key": "10.4337/9781035371341"}];

const out = [];

async function fetchCrossref(doi) {
  const r = await fetch(`https://api.crossref.org/works/${encodeURIComponent(doi)}`, {
    headers: {"User-Agent": "Mancano-Zotero-cleanup/1.0 (mailto:talesmanz01@gmail.com)"}
  });
  if (!r.ok) throw new Error(`CrossRef ${r.status}`);
  const j = await r.json();
  return j.message;
}

async function fetchOpenLibrary(isbn) {
  const key = `ISBN:${isbn.replace(/[^0-9Xx]/g,'')}`;
  const r = await fetch(`https://openlibrary.org/api/books?bibkeys=${encodeURIComponent(key)}&format=json&jscmd=data`);
  if (!r.ok) throw new Error(`OpenLibrary ${r.status}`);
  const j = await r.json();
  return j[key];
}

function setIfEmpty(item, field, value) {
  if (!value) return false;
  try {
    const cur = item.getField(field);
    if (cur && String(cur).trim() !== "") return false;
    item.setField(field, String(value));
    return true;
  } catch(e) { return false; }
}

async function enrichDOI(item, doi) {
  const m = await fetchCrossref(doi);
  let touched = [];
  if (m.title && m.title[0]) {
    if (setIfEmpty(item, "title", m.title[0])) touched.push("title");
  }
  if (m["container-title"] && m["container-title"][0]) {
    if (setIfEmpty(item, "publicationTitle", m["container-title"][0])) touched.push("publicationTitle");
  }
  if (m.publisher && setIfEmpty(item, "publisher", m.publisher)) touched.push("publisher");
  if (m.volume && setIfEmpty(item, "volume", m.volume)) touched.push("volume");
  if (m.issue && setIfEmpty(item, "issue", m.issue)) touched.push("issue");
  if (m.page && setIfEmpty(item, "pages", m.page)) touched.push("pages");
  if (m.abstract && setIfEmpty(item, "abstractNote", m.abstract.replace(/<[^>]+>/g,""))) touched.push("abstractNote");
  const dp = m["published-print"] || m["published-online"] || m["issued"];
  if (dp && dp["date-parts"] && dp["date-parts"][0]) {
    const date = dp["date-parts"][0].join("-");
    if (setIfEmpty(item, "date", date)) touched.push("date");
  }
  if (item.getCreators().length === 0 && m.author) {
    const creators = m.author.map(a => ({
      firstName: a.given || "",
      lastName: a.family || a.name || "",
      creatorType: "author"
    })).filter(c => c.firstName || c.lastName);
    if (creators.length) {
      item.setCreators(creators);
      touched.push(`creators(${creators.length})`);
    }
  }
  return touched;
}

async function enrichISBN(item, isbn) {
  const data = await fetchOpenLibrary(isbn);
  if (!data) return [];
  let touched = [];
  if (data.title && setIfEmpty(item, "title", data.title)) touched.push("title");
  if (data.publish_date && setIfEmpty(item, "date", data.publish_date)) touched.push("date");
  if (data.publishers && data.publishers[0] && setIfEmpty(item, "publisher", data.publishers[0].name)) touched.push("publisher");
  if (data.publish_places && data.publish_places[0] && setIfEmpty(item, "place", data.publish_places[0].name)) touched.push("place");
  if (data.number_of_pages && setIfEmpty(item, "numPages", String(data.number_of_pages))) touched.push("numPages");
  if (data.notes && setIfEmpty(item, "abstractNote", data.notes)) touched.push("abstractNote");
  if (item.getCreators().length === 0 && data.authors) {
    const creators = data.authors.map(a => {
      const name = a.name || "";
      const parts = name.trim().split(/\s+/);
      const last = parts.pop() || "";
      const first = parts.join(" ");
      return { firstName: first, lastName: last, creatorType: "author" };
    }).filter(c => c.firstName || c.lastName);
    if (creators.length) {
      item.setCreators(creators);
      touched.push(`creators(${creators.length})`);
    }
  }
  return touched;
}

const total = ITEMS.length;
let ok = 0, fail = 0;
out.push(`=== BALDE A: enrich ${total} itens ===`);

for (let i = 0; i < ITEMS.length; i++) {
  const spec = ITEMS[i];
  try {
    const item = await Zotero.Items.getAsync(spec.id);
    if (!item) { out.push(`[${spec.id}] NÃO ENCONTRADO`); fail++; continue; }
    let touched = [];
    if (spec.action === "enrich_via_doi") {
      touched = await enrichDOI(item, spec.lookup_key);
    } else if (spec.action === "enrich_via_isbn") {
      touched = await enrichISBN(item, spec.lookup_key);
    }
    if (touched.length) {
      await item.saveTx();
      out.push(`[${spec.id}] ✓ ${touched.join(", ")}`);
      ok++;
    } else {
      out.push(`[${spec.id}] — nada a preencher`);
    }
  } catch (e) {
    out.push(`[${spec.id}] ✗ ERRO: ${e.message || e}`);
    fail++;
  }
  if ((i+1) % 10 === 0) await Zotero.Promise.delay(1000);
  else await Zotero.Promise.delay(250);
}

out.push(`=== Resultado: ${ok} enriquecidos, ${fail} falhas, ${total-ok-fail} sem mudança ===`);
return out.join("\n");
