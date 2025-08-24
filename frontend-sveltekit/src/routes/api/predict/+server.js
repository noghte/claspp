import { json, text } from '@sveltejs/kit';

/**
 * Very small FASTA parser and 21-mer slicer compatible with your backend.
 * Pads with 10 '-' on each side. Produces every 21-mer window.
 */
function parseFastaOrRawToPeptides(input) {
  const seqs = [];
  const lines = input.split(/\r?\n/);
  let cur = null;
  for (const line of lines) {
    if (!line) continue;
    if (line[0] === '>') {
      if (cur && cur.seq) seqs.push(cur.seq);
      cur = { id: line.slice(1).trim(), seq: '' };
    } else {
      const chunk = line.trim().toUpperCase();
      if (!cur) cur = { id: 'seq', seq: '' };
      cur.seq += chunk;
    }
  }
  if (cur && cur.seq) seqs.push(cur.seq);

  // If it wasn't FASTA, treat whole input as a single raw sequence block
  if (seqs.length === 0) {
    const raw = input.trim().toUpperCase();
    if (raw) seqs.push(raw.replace(/\s+/g, ''));
  }

  const peptides = [];
  const pad = '-'.repeat(10);
  for (const s of seqs) {
    const padded = pad + s + pad;
    for (let i = 0; i < s.length; i++) {
      peptides.push(padded.slice(i, i + 21));
    }
  }
  return peptides;
}

const LABELS = [
  'S_Phosphorylation','T_Phosphorylation','K_Ubiquitination','Y_Phosphorylation',
  'K_Acetylation','N_N-linked-Glycosylation','S_O-linked-Glycosylation','T_O-linked-Glycosylation',
  'R_Methylation','K_Methylation','K_Sumoylation','K_Malonylation','M_Sulfoxidation',
  'A_Acetylation','M_Acetylation','C_Glutathionylation','C_S-palmitoylation',
  'P_Hydroxylation','K_Hydroxylation','NegLab'
];

const BACKEND = 'http://172.22.150.196:5300/api/predict';
const MAX_PEPS = 2000;  // keep payloads sane

export async function POST({ request }) {
  try {
    const ct = request.headers.get('content-type') || '';
    let fastaOrRaw = '';

    if (ct.includes('multipart/form-data')) {
      const form = await request.formData();
      const file = form.get('file');
      const seq = form.get('sequence');
      if (file && typeof file.text === 'function') {
        fastaOrRaw = await file.text();
      } else if (seq && typeof seq === 'string') {
        fastaOrRaw = seq;
      } else {
        return text('Please upload a FASTA or paste a sequence.', { status: 400 });
      }
    } else if (ct.includes('application/json')) {
      const body = await request.json();
      fastaOrRaw = (body.sequence || '').toString();
    } else {
      fastaOrRaw = await request.text();
    }

    const peptides = parseFastaOrRawToPeptides(fastaOrRaw).slice(0, MAX_PEPS);
    if (peptides.length === 0) {
      return text('No peptides generated. Check your input.', { status: 400 });
    }

    // Proxy to backend
    const resp = await fetch(BACKEND, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ peptides })
    });
    if (!resp.ok) {
      const t = await resp.text();
      return text(`Backend error ${resp.status}: ${t}`, { status: 502 });
    }
    const pred = await resp.json(); // [{ peptide, scores: {...}}]

    // Build CSV expected by your UI
    let csv = 'pep,' + LABELS.join(',') + '\n';
    for (const row of pred) {
      const vals = LABELS.map(l => {
        const v = row.scores?.[l];
        return typeof v === 'number' ? String(v) : '';
        });
      csv += `${row.peptide},${vals.join(',')}\n`;
    }

    return new Response(csv, {
      status: 200,
      headers: { 'content-type': 'text/csv; charset=utf-8' }
    });
  } catch (e) {
    console.error('predict endpoint error', e);
    return text('Internal Server Error', { status: 500 });
  }
}