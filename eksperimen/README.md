# Eksperimen Code Review Agent AI (`shopapp`)

Folder ini berisi kode, prompt, dataset, dan hasil mentah eksperimen yang membandingkan tiga cara mereview kode Python:

1. **Analisis statis**: Pylint (`--disable=C,R`), Bandit, Ruff (`--select F,B,S`), serta gabungan ketiganya.
2. **LLM single-shot** (`single`): `claude -p --model sonnet --tools ""`. Isi file bernomor baris ditempel ke prompt, tanpa tools.
3. **Code review agent** (`agent`): `claude -p --model sonnet --tools Read,Grep,Glob`. Agent hanya diberi nama file, lalu menelusuri konteks proyek dan memverifikasi temuannya sendiri.

Dokumentasi lengkap ada di [`../docs/`](../docs/README.md).

## Isi folder

| Path | Isi |
| --- | --- |
| `dataset/shopapp/` | 14 file Python (290 baris): 12 file dengan 22 cacat tertanam, 2 file bersih (`money.py`, `task_queue.py`) |
| `ground_truth.json` | 22 cacat `D01`–`D22`: file, anchor teks, kategori, deskripsi |
| `prompts/single_shot.txt`, `prompts/agent.txt` | Prompt persis yang dikirim ke model |
| `common.py` | Path, pemuatan ground truth (anchor → nomor baris), pencocokan temuan satu-satu dengan toleransi ±2 baris |
| `run_static.py` | Menjalankan Pylint, Bandit, Ruff → `results/static_<tool>.json` |
| `run_llm.py` | Menjalankan kondisi `single` dan `agent` di salinan terisolasi; opsi `--retry-failed` untuk mengulang file yang gagal kuota |
| `evaluate.py` | Precision, recall, F1, FP di file bersih, rata-rata ± simpangan baku 3 run, ablasi severity dan konsensus, recall per kategori, matriks per cacat; `--md` menulis ringkasan |
| `results/` | 9 JSON mentah (3 statis, 3 run × 2 kondisi LLM) dan `summary.md` |
| `results_llm_log.txt`, `results_llm_retry_log.txt` | Log eksekusi pertama dan pengulangan |

## Menjalankan

```bash
cd eksperimen
pip install pylint bandit ruff
python run_static.py                       # baseline statis
python run_llm.py 1 sonnet                 # satu run LLM (butuh claude CLI)
python run_llm.py 1 sonnet --retry-failed  # ulangi file yang gagal kuota
python evaluate.py --md results/summary.md # hitung semua metrik
```
