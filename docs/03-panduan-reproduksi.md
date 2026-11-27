# 03 — Panduan Reproduksi dan Troubleshooting

Langkah menyiapkan lingkungan, menjalankan baseline statis, menjalankan eksperimen LLM, dan menghitung ulang metrik.

## 1. Prasyarat

| Komponen | Versi yang dipakai | Kegunaan |
| --- | --- | --- |
| Python | 3.14.6 (3.10+ seharusnya cukup) | Menjalankan semua skrip |
| Pylint | 4.1.4 | Baseline linter |
| Bandit | 1.9.4 | Baseline SAST keamanan |
| Ruff | 0.17.6 | Baseline linter (aturan F, B, S) |
| Claude Code CLI | 2.1.318, sudah login | Menjalankan kondisi `single` dan `agent` (`claude -p`) |

```bash
pip install pylint bandit ruff
```

Semua perintah di bawah dijalankan dari folder `eksperimen/`.

## 2. Menghitung ulang metrik (tanpa memanggil API)

Data mentah semua run sudah ada di `results/`.

```bash
python evaluate.py                      # cetak semua tabel
python evaluate.py --md results/summary.md   # juga simpan sebagai Markdown
```

## 3. Menjalankan ulang baseline statis

```bash
python run_static.py
```

Menjalankan `pylint --disable=C,R`, `bandit`, dan `ruff check --select F,B,S` pada 14 file, lalu menulis `results/static_<tool>.json`.

## 4. Menjalankan ulang eksperimen LLM

Butuh `claude` di `PATH` dan kuota yang cukup. Satu run penuh = 28 panggilan (14 file × 2 kondisi). Biaya rata-rata per run: sekitar USD 0,14 untuk `single` dan USD 4,10 untuk `agent`.

```bash
# python run_llm.py <run_id> [model] [--retry-failed]
python run_llm.py 1 sonnet
python run_llm.py 2 sonnet
python run_llm.py 3 sonnet
```

Yang dilakukan `run_llm.py`:
- Menyalin `dataset/shopapp/` ke folder sementara `crx_*`, supaya agent tidak bisa membaca `ground_truth.json`.
- Menjalankan 4 pekerjaan paralel, batas waktu 900 detik per file.
- Menulis `results/llm_single_run<id>.json` dan `results/llm_agent_run<id>.json`.

## 5. Troubleshooting

1. **Limit kuota (`You've hit your 5-hour limit`).**
   Gejala: `findings` kosong, `cost_usd` 0, dan `raw` berisi pesan limit. Ini terjadi pada eksekusi pertama (3 file di agent run 2 dan seluruh run 3).
   Solusi: tunggu kuota reset, lalu ulangi hanya file yang gagal:
   ```bash
   python run_llm.py 3 sonnet --retry-failed
   ```
   Hasilnya digabung ke file JSON yang sudah ada. `evaluate.py` tidak pernah menghitung review yang gagal; run yang belum lengkap ditandai "tidak lengkap".
2. **Mengubah dataset.** Jangan mengubah teks `anchor` di `ground_truth.json` kecuali disengaja. `common.ground_truth()` akan gagal (`AssertionError`) jika anchor tidak ditemukan di file.
3. **Mengganti model.** Argumen kedua `run_llm.py` diteruskan ke `claude --model`, misalnya `opus` atau `haiku`. Simpan hasilnya dengan `run_id` berbeda agar tidak menimpa run lama.
