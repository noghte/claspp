# app.py
from flask import Flask, request, abort
from flask_cors import CORS
import logging, os, io, tempfile
import torch
import torch.nn as nn
import numpy as np

from transformers import EsmTokenizer
from modeling_esm import EsmForSequenceClassificationCustomWidehead

app = Flask(__name__)
env = os.environ['FLASK_ENV'] if 'FLASK_ENV' in os.environ else "production"
print(env)

CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "expose_headers": ["Access-Control-Allow-Private-Network"],
        "allow_private_network": True
    }
})

logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# -----------------------------
# Model init
# -----------------------------
MODEL_DIR = os.environ.get("MODEL_DIR", "finalCheckpoint_25_05_11/")
NUM_LABELS = 54
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", "50"))

print("initializing checkpoint")
tokenizer = EsmTokenizer.from_pretrained(MODEL_DIR)
model = EsmForSequenceClassificationCustomWidehead.from_pretrained(
    MODEL_DIR, num_labels=NUM_LABELS
).to(DEVICE).eval()
sigmoid = nn.Sigmoid().to(DEVICE)
print("finished downloading")

# -----------------------------
# Label mapping and helpers
# -----------------------------
# Indices into the 54-logit vector are reduced to 20 outputs using max pooling over groups.
# Final CSV column order is position index 0..19 as defined here:
pos2lab = {
    0: "S_Phosphorylation",
    1: "T_Phosphorylation",
    2: "K_Ubiquitination",
    3: "Y_Phosphorylation",
    4: "K_Acetylation",
    5: "N_N-linked-Glycosylation",
    6: "S_O-linked-Glycosylation",
    7: "T_O-linked-Glycosylation",
    8: "R_Methylation",
    9: "K_Methylation",
    10: "K_Sumoylation",
    11: "K_Malonylation",
    12: "M_Sulfoxidation",
    13: "A_Acetylation",
    14: "M_Acetylation",
    15: "C_Glutathionylation",
    16: "C_S-palmitoylation",
    17: "P_Hydroxylation",
    18: "K_Hydroxylation",
    19: "NegLab",
}
lab_header = ["pep"] + [pos2lab[i] for i in range(20)]

def fasta_to_list(fasta_str: str):
    """Parse FASTA text to list of (id, seq)."""
    seqs = []
    curr_id, curr_seq = None, []
    for line in fasta_str.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            if curr_id is not None:
                seqs.append((curr_id, "".join(curr_seq)))
            curr_id = line[1:].strip()
            curr_seq = []
        else:
            curr_seq.append(line)
    if curr_id is not None:
        seqs.append((curr_id, "".join(curr_seq)))
    return seqs

def scrape_21mers_from_full(seq: str):
    """Pad with 10 '-' both sides and extract all 21-mers. De-duplicate."""
    padded = "-"*10 + seq + "-"*10
    peps = [padded[i:i+21] for i in range(len(seq))]
    return list(dict.fromkeys(peps))  # stable de-dup

def preprocess_str(pep: str):
    """Match training-time normalization: '.'->'<mask>', '-'->'<pad>'."""
    return pep.replace(".", "<mask>").replace("-", "<pad>")

@torch.no_grad()
def model_predict(peptides: list[str], batch_size: int = BATCH_SIZE):
    """Return raw 54-d probabilities per peptide."""
    probs = []
    for i in range(0, len(peptides), batch_size):
        batch = peptides[i:i+batch_size]
        enc = tokenizer(batch, padding=True, return_tensors="pt")
        enc = {k: v.to(DEVICE) for k, v in enc.items()}
        logits = model(enc["input_ids"], enc["attention_mask"])["logits"]
        p = sigmoid(logits).detach().cpu().numpy()  # (B, 54)
        probs.extend(p.tolist())
    return probs  # list of 54-floats

def reduce_to_20(elab: np.ndarray, center_res: str):
    """Apply the same grouping logic as getlab in your script."""
    out = np.zeros((20,), dtype=float)

    # ST-Phosphorylation [0:5] => split by center residue
    if center_res == "S":
        out[0] = float(np.max(elab[0:5]))
    elif center_res == "T":
        out[1] = float(np.max(elab[0:5]))

    # K-Ubiquitination [5:25]
    out[2] = float(np.max(elab[5:25]))

    # Y-Phosphorylation [25:26]
    out[3] = float(np.max(elab[25:26]))

    # K-Acetylation [26:36]
    out[4] = float(np.max(elab[26:36]))

    # N-N-linked-Glycosylation [36:37]
    out[5] = float(np.max(elab[36:37]))

    # ST-O-linked-Glycosylation [37:42] => split by S/T
    if center_res == "S":
        out[6] = float(np.max(elab[37:42]))
    elif center_res == "T":
        out[7] = float(np.max(elab[37:42]))

    # RK-Methylation [42:46] => split by R/K
    if center_res == "R":
        out[8] = float(np.max(elab[42:46]))
    elif center_res == "K":
        out[9] = float(np.max(elab[42:46]))

    # K-Sumoylation [46:47]
    out[10] = float(np.max(elab[46:47]))

    # K-Malonylation [47:48]
    out[11] = float(np.max(elab[47:48]))

    # M-Sulfoxidation [48:49]
    out[12] = float(np.max(elab[48:49]))

    # AM-Acetylation [49:50] => split by A/M
    if center_res == "A":
        out[13] = float(np.max(elab[49:50]))
    elif center_res == "M":
        out[14] = float(np.max(elab[49:50]))

    # C-Glutathionylation [50:51]
    out[15] = float(np.max(elab[50:51]))

    # C-S-palmitoylation [51:52]
    out[16] = float(np.max(elab[51:52]))

    # PK-Hydroxylation [52:53] => split by P/K
    if center_res == "P":
        out[17] = float(np.max(elab[52:53]))
    elif center_res == "K":
        out[18] = float(np.max(elab[52:53]))

    # NegLab [53:54]
    out[19] = float(np.max(elab[53:54]))

    return out

def to_csv(peps: list[str], probs54: list[list[float]]):
    """Build CSV text with header and reduced 20 outputs per peptide."""
    lines = [",".join(lab_header)]
    for pep, p in zip(peps, probs54):
        center_res = pep[10] if len(pep) >= 11 else ""  # center of 21-mer
        out20 = reduce_to_20(np.array(p, dtype=float), center_res)
        row = [pep] + [f"{v:.6g}" for v in out20.tolist()]
        lines.append(",".join(row))
    return "\n".join(lines) + "\n"

# -----------------------------
# Routes
# -----------------------------
@app.route('/api/')
def test():
    return 'Server is running!'

@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Predict PTM probabilities for input sequences.
    Accepts multipart/form-data with either:
      - 'file': FASTA text of one or more sequences
      - 'sequence': a single raw sequence string
    Returns CSV text with columns: pep,<20 labels>
    """
    # Collect sequences
    seq_items = []  # list[(id, seq)]
    if 'file' in request.files:
        fasta_bytes = request.files['file'].read()
        try:
            fasta_str = fasta_bytes.decode('utf-8')
        except Exception:
            abort(400, 'File must be UTF-8 text')
        seq_items = fasta_to_list(fasta_str)
    else:
        seq = request.form.get('sequence', '').strip()
        if not seq:
            abort(400, 'No sequence or file provided')
        seq_items = [('sequence_1', seq)]

    if not seq_items:
        abort(400, 'No valid sequences found')

    # Build peptide list: if length >= 21, scrape 21-mers. If already 21, use as-is.
    peptides = []
    for _sid, seq in seq_items:
        seq = seq.strip()
        if len(seq) >= 21:
            peptides.extend(scrape_21mers_from_full(seq))
        else:
            abort(400, 'Sequence must be at least 21 aa long or provide 21-mer peptides')

    # Normalize tokens to match training preprocessing
    pep_norm = [preprocess_str(p) for p in peptides]

    try:
        torch.cuda.empty_cache()
        probs54 = model_predict(pep_norm, batch_size=BATCH_SIZE)
        csv_text = to_csv(peptides, probs54)
        return app.response_class(csv_text, mimetype='text/csv')
    except Exception as e:
        logging.exception("Model prediction failed")
        abort(500, f"Model prediction failed: {e}")

if __name__ == '__main__':
    # Example run:
    # MODEL_DIR=finalCheckpoint_25_05_11/ FLASK_ENV=development python app.py
    app.run(debug=False, host="0.0.0.0", port=5200)