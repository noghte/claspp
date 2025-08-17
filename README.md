# CLASPP: Contrastively learned attention based stratified PTM predictor

This project provides a web application and service to predict post-translational modification (PTM) likelihoods for protein sequences. The model is hosted as a service in the OS and performs multi-label classification across diverse PTM types. Users can submit a FASTA file or a raw sequence and obtain a CSV output, where columns correspond to recognized PTM labels and each row contains predictions for one input sequence.

## Example Output

```csv
pep,S_Phosphorylation,T_Phosphorylation,K_Ubiquitination,Y_Phosphorylation,K_Acetylation,N_N-linked-Glycosylation,S_O-linked-Glycosylation,T_O-linked-Glycosylation,R_Methylation,K_Methylation,K_Sumoylation,K_Malonylation,M_Sulfoxidation,A_Acetylation,M_Acetylation,C_Glutathionylation,C_S-palmitoylation,P_Hydroxylation
VASLEESEGNKQDLKALKEAV,0.0,0.0,0.9414424300193787,1.39e-13,0.1694029123,1.40e-07,0.0,0.0,0.0,0.001010334,0.023382623,0.073079787,2.01e-11,0.0,0.0,9.53e-08,2.91e-07,0.0,5.21e-06,0.000342548
KVYTIRPYFPKDEASVYKICR,0.0,0.0,0.8317223787,2.54e-09,0.2771511376,1.47e-07,0.0,0.0,0.0,0.070256226,0.023312218,0.036413942,3.39e-09,0.0,0.0,1.03e-08,6.51e-09,0.0,7.67e-06,0.006396129
```

## Usage

1. Start the backend service:

```bash
cd backend-flask
pip install -r requirements.txt
export MODEL_CMD=claspp_predict  # optional, defaults to 'claspp_predict'
python app.py
```

2. Start the frontend application:

```bash
cd frontend-sveltekit
npm install
npm run dev
```

3. Open your browser at `http://localhost:5173` (or the port shown) to access the CLASPP web interface.

## Requirements

- Python 3.8+ (backend)
- Node.js 16.x or 18.x LTS (frontend). Node.js 23+ may have ESM resolution issues; use an LTS version (e.g., 16.x or 18.x).

## License

This project is provided under the MIT License.
