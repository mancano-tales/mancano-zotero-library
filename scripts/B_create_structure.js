// Script B — Criação da estrutura v5 (56 coleções)
// Data de criação: 2026-05-10
// Data de execução: 2026-05-10
// Status: EXECUTADO
// Output esperado: lista de coleções criadas
//
// Resultado real: Created 56 collections (vide NEWS.md).
//
// Idempotente: se rodar de novo, pula as que já existem.

const lib = Zotero.Libraries.userLibraryID;
const created = [];

async function mk(name, parent) {
  const siblings = parent
    ? parent.getChildCollections()
    : Zotero.Collections.getByLibrary(lib).filter(c => !c.parentID);
  const exists = siblings.find(c => c.name === name);
  if (exists) return exists;
  const c = new Zotero.Collection();
  c.libraryID = lib;
  c.name = name;
  if (parent) c.parentID = parent.id;
  await c.saveTx();
  created.push(name);
  return c;
}

// 1. Active Research
const r1 = await mk('1. Active Research');
await mk("Master's — ProUni & Affirmative Action", r1);
await mk('BEPE — Tarlau (2026)', r1);
await mk('Methods Workshop (2026)', r1);
await mk('IC FFLCH — Victor Alcantara', r1);

// 2. Workbench
await mk('2. Workbench');

// 3. Fields
const r3 = await mk('3. Fields');

const tm = await mk('★ Theory & Methodology', r3);
const tmT = await mk('Theory', tm);
await mk('Ontology & Epistemology', tmT);
const par = await mk('Theoretical Paradigms', tmT);
await mk('Analytical Sociology', par);
await mk('Historical Institutionalism', par);
await mk('Marxism', par);
await mk('Reproduction Theory & Bourdieu', par);
await mk('Varieties of Capitalism', par);
await mk('Welfare State Theory', par);
const tmM = await mk('Methodology', tm);
await mk('Causal Inference & Econometrics', tmM);
await mk('Comparative-Historical & Process Tracing', tmM);
await mk('Qualitative Methods', tmM);
await mk('Research Design', tmM);

const econ = await mk('Economics', r3);
await mk('Economic History', econ);
await mk('Economics of Education & Human Capital', econ);
await mk('Economics of Inequality', econ);
await mk('Industrial Organization & Antitrust', econ);
await mk('Political Economy & Institutional Economics', econ);

const edu = await mk('Education', r3);
await mk('Affirmative Action & Quotas', edu);
await mk('Comparative Cases', edu);
await mk('Higher Education — Brazil', edu);
await mk('History of Education — Brazil', edu);
await mk('History of Education — Comparative', edu);

const ps = await mk('Political Science', r3);
await mk('Brazilian Politics', ps);
await mk('Comparative Politics — Empirical', ps);
await mk('Democracy, Inequality & Distribution', ps);
await mk('State, Business & Industrial Policy', ps);
await mk('Welfare States & Social Policy', ps);

const soc = await mk('Sociology', r3);
const bst = await mk('Brazilian Social Thought', soc);
await mk('Florestan Fernandes', bst);
await mk('Economic Sociology', soc);
await mk('Social Stratification & Mobility', soc);
await mk('Sociology of Education', soc);

// 4. Coursework
await mk('4. Coursework');

// 5. Bureaucracy & Documents
const r5 = await mk('5. Bureaucracy & Documents');
await mk('CVs', r5);
await mk('My Documents', r5);
await mk('Other Records', r5);
await mk('Recommendation Letters', r5);
await mk('Syllabuses', r5);

// 6, 7, 9
await mk('6. Leisure Reading');
await mk('7. Misc');
await mk('9. Archive');

return `Created ${created.length} collections.\n\n` + created.map(n => '+ ' + n).join('\n');
