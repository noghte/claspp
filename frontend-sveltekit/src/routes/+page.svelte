<section class="mx-auto max-w-3xl px-6 py-12">
  <h1 class="text-3xl sm:text-4xl font-semibold tracking-tight">
    <span class="bg-gradient-to-r from-black to-zinc-600 bg-clip-text text-transparent">
      Abstract
    </span>
  </h1>

  <p class="mt-6 text-zinc-700 leading-7">
    Post-translational modifications (PTMs) regulate protein function and cell signaling, yet accurate residue-level prediction remains challenging across diverse PTM types. CLASPP is a contrastively learned, attention-based model that integrates protein sequence embeddings with PTM-specific stratified heads. Contrastive pretraining separates modified and unmodified contexts. Multi-head attention highlights sequence motifs and provides residue-level saliency for interpretation. CLASPP delivers calibrated probabilities, supports common and rare PTMs, and generalizes under strict cross-protein splits. In benchmarks across phosphorylation, acetylation, ubiquitination, and glycosylation tasks, CLASPP matches or exceeds strong baselines while producing interpretable attention maps. We release model weights, training code, and an API for large-scale screening.
  </p>

  <!-- <div class="mt-6 flex flex-wrap items-center gap-3">
    <span class="inline-flex items-center rounded-full bg-zinc-100 px-3 py-1 text-sm text-zinc-700">
      Contrastive learning
    </span>
    <span class="inline-flex items-center rounded-full bg-zinc-100 px-3 py-1 text-sm text-zinc-700">
      Multi-head attention
    </span>
    <span class="inline-flex items-center rounded-full bg-zinc-100 px-3 py-1 text-sm text-zinc-700">
      Post-translational modifications
    </span>
    <span class="inline-flex items-center rounded-full bg-zinc-100 px-3 py-1 text-sm text-zinc-700">
      PTM prediction
    </span>
  </div> -->

  <div class="mt-8 flex flex-wrap gap-3">
    <a href="/paper.pdf" class="rounded-lg border border-zinc-300 px-4 py-2 text-sm font-medium hover:bg-zinc-50">Read the paper</a>
    <a href="https://github.com/gravelCompBio/Claspp_forward/" class="rounded-lg bg-black px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800">View on GitHub</a>
    <a href="/claspp/prediction" class="rounded-lg border border-zinc-300 px-4 py-2 text-sm font-medium hover:bg-zinc-50">Prediction</a>
  </div>
  <br />

  <img src="/architecture.png" alt="CLASPP architecture" class="mt-8 mb-6" />

</section>