<script>
  import { base } from '$app/paths';

  let currentSeq = '';
  let files;
  let processing = false;

  let predRows = null;
  let rawCsvText = '';
  let csvHeader = [];

  function handleFilePick() {
    document.getElementById('file')?.click();
  }
  function clearFile() {
    files = undefined;
  }

  async function predict() {
    processing = true;
    predRows = null;
    rawCsvText = '';
    csvHeader = [];

    try {
      const api = `${window.location.origin}${base}/api/predict`;
      const fd = new FormData();

      if (files && files[0]) {
        fd.append('file', files[0]);
      } else {
        const seq = (currentSeq || '').trim();
        if (!seq) throw new Error('Please upload a FASTA or paste a sequence.');
        fd.append('sequence', seq);
      }

      const resp = await fetch(api, { method: 'POST', body: fd });
      if (!resp.ok) throw new Error(`Server error ${resp.status}: ${await resp.text()}`);

      const text = await resp.text();
      rawCsvText = text;

      const { header, rows } = parseCsv(text);
      csvHeader = header;
      predRows = rows;
    } catch (e) {
      console.error(e);
      alert(e.message || 'Prediction failed');
    } finally {
      processing = false;
    }
  }

  function parseCsv(text) {
    const lines = text.trim().split(/\r?\n/).filter(Boolean);
    if (!lines.length) return { header: [], rows: [] };
    const header = lines[0].split(',');
    const rows = lines.slice(1).map(line => {
      const cols = line.split(',');
      const obj = {};
      header.forEach((h, i) => (obj[h] = cols[i]));
      return obj;
    });
    return { header, rows };
  }

  function topK(row, k = 3, minScore = 0.0) {
    if (!row) return [];
    return Object.entries(row)
      .filter(([name]) => name !== 'pep')
      .map(([name, v]) => ({ name, value: parseFloat(v) }))
      .filter(d => !Number.isNaN(d.value) && d.value >= minScore)
      .sort((a, b) => b.value - a.value)
      .slice(0, k);
  }

  function downloadCSV() {
    if (!rawCsvText) return;
    const blob = new Blob([rawCsvText], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'predictions.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }
</script>

<section class="mx-auto max-w-5xl px-6 py-10">
  <!-- Header -->
  <header class="mb-8">
    <h2 class="text-xl font-semibold tracking-tight text-zinc-900">Sequence Input</h2>
    <p class="mt-2 text-sm text-zinc-600">Upload a FASTA file or paste a raw sequence.</p>
  </header>

  <!-- Input Card -->
  <div class="grid gap-6 md:grid-cols-2">
    <div class="rounded-2xl border border-zinc-200 bg-white/70 p-5 shadow-sm">
      <label class="block text-sm font-medium text-zinc-800">FASTA file</label>

      <input
        id="file"
        type="file"
        class="hidden"
        accept=".fasta,.fa,.fna,.ffn,.faa,.frn"
        bind:files
      />

      <div class="mt-2 flex items-center gap-3">
        <button
          on:click={handleFilePick}
          type="button"
          class="inline-flex items-center rounded-lg bg-zinc-900 px-3 py-2 text-sm font-medium text-white hover:bg-zinc-800"
        >
          Upload FASTA
        </button>

        {#if files && files[0]}
          <span class="truncate text-sm text-zinc-700 max-w-[220px]">{files[0].name}</span>
          <button
            type="button"
            on:click={clearFile}
            class="text-xs text-zinc-600 hover:text-zinc-900 underline"
          >
            Clear
          </button>
        {/if}
      </div>

      <div class="mt-5">
        <label class="mb-1 block text-sm font-medium text-zinc-800">Sequence</label>
        <textarea
          rows="10"
          bind:value={currentSeq}
          placeholder=">id&#10;MSTAVAVL...K"
          class="w-full resize-y rounded-lg border border-zinc-300 bg-zinc-50 p-3 font-mono text-sm text-zinc-800 outline-none ring-0 focus:border-zinc-400 focus:bg-white"
        />
        <p class="mt-2 text-xs text-zinc-500">Pasting a sequence overrides file upload.</p>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex flex-col justify-between rounded-2xl border border-zinc-200 bg-white/70 p-5 shadow-sm">
      <div class="space-y-3">
        <h3 class="text-sm font-medium text-zinc-800">Run prediction</h3>
        <p class="text-sm text-zinc-600">Submit either a FASTA file or a pasted sequence.</p>
      </div>

      <div class="mt-6 flex items-center gap-3 md:mt-0 md:justify-end">
        {#if !processing}
          <button
            on:click={predict}
            type="button"
            class="inline-flex items-center rounded-lg bg-red-700 px-4 py-2 text-sm font-medium text-white hover:bg-red-800"
          >
            Predict
          </button>
        {:else}
          <button
            type="button"
            disabled
            class="inline-flex items-center rounded-lg bg-red-700 px-4 py-2 text-sm font-medium text-white opacity-80"
          >
            <span class="mr-2 inline-block h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></span>
            Processing...
          </button>
        {/if}
      </div>
    </div>
  </div>

  <!-- Results -->
  {#if predRows}
    <div class="mt-10 rounded-2xl border border-zinc-200 bg-white/70 p-5 shadow-sm">
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-semibold text-zinc-900">Predictions</h2>
        <button
          on:click={downloadCSV}
          type="button"
          class="inline-flex items-center rounded-lg border border-zinc-300 px-3 py-1.5 text-sm font-medium text-zinc-800 hover:bg-zinc-50"
        >
          Download CSV
        </button>
      </div>

      <div class="mt-4 overflow-x-auto">
        <table class="min-w-full border-separate border-spacing-0">
          <thead class="sticky top-0">
            <tr>
              <th class="bg-zinc-100 py-2 pl-4 pr-3 text-left text-sm font-medium text-zinc-800 first:rounded-tl-xl">Peptide (21-mer)</th>
              <th class="bg-zinc-100 py-2 px-3 text-left text-sm font-medium text-zinc-800 last:rounded-tr-xl">Top labels (score)</th>
            </tr>
          </thead>
          <tbody class="[&>tr:nth-child(even)]:bg-zinc-50">
            {#each predRows as row, idx (idx)}
              <tr class="align-top">
                <td class="whitespace-pre-wrap py-2 pl-4 pr-3 text-sm font-mono text-zinc-900">{row.pep}</td>
                <td class="py-2 px-3 text-sm text-zinc-800">
                  {#each topK(row, 3, 0.0) as kv}
                    <span class="mr-3 inline-flex items-center rounded-md bg-zinc-100 px-2 py-0.5">{kv.name}: {Number(kv.value).toFixed(4)}</span>
                  {/each}
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </div>
  {/if}
</section>