# 04 — Log Hasil Lengkap dan Ablasi

Semua angka di dokumen ini dihasilkan oleh [`eksperimen/evaluate.py`](../eksperimen/evaluate.py) dari data mentah di [`eksperimen/results/`](../eksperimen/results/). Versi tabel yang selalu terbaru: [`eksperimen/results/summary.md`](../eksperimen/results/summary.md) (dibuat dengan `python evaluate.py --md results/summary.md`).

## Catatan penting sebelum membaca angka

1. **Semua run LLM lengkap (3 × 14 file per kondisi).** Pada eksekusi pertama, limit kuota Claude Code menghentikan 3 file di agent run 2 (`stats.py`, `task_queue.py`, `user_repo.py`) dan seluruh run 3. File-file itu dijalankan ulang dengan prompt dan model yang sama memakai `python run_llm.py <run> sonnet --retry-failed` (log: `results_llm_retry_log.txt`). Review yang gagal tidak pernah dihitung sebagai hasil; `evaluate.py` menandai run tidak lengkap secara eksplisit.
2. **Validasi semantik.** Pencocokan memakai file + selisih baris ≤ 2, lalu isi setiap TP diperiksa. Seluruh 132 TP LLM (2 kondisi × 3 run × 22) membahas cacat yang benar. Satu temuan Pylint (`report.py:21`, `W1514 unspecified-encoding`) kebetulan jatuh di baris D19 tetapi membahas parameter encoding, bukan file yang tidak ditutup, sehingga dihitung **FP**. Akibatnya recall Pylint 3/22 (bukan 4/22) dan statis gabungan 9/22 (bukan 10/22). Aturan ini ada di `SEMANTIC_MISMATCH` pada `evaluate.py`.
3. **Waktu** = jumlah durasi per file (run sebenarnya paralel 4 pekerja). **Biaya** = `total_cost_usd` dari keluaran `claude -p --output-format json`.

## Tabel 1. Hasil per metode dan per run

| Metode | Run | Temuan | TP | FP | FN | Precision | Recall | F1 | FP file bersih | Waktu (s) | Biaya (USD) | Rata-rata turn |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| pylint | - | 4 | 3 | 1 | 19 | 0.750 | 0.136 | 0.231 | 0 | 1.75 | 0 | - |
| bandit | - | 8 | 7 | 1 | 15 | 0.875 | 0.318 | 0.467 | 0 | 0.79 | 0 | - |
| ruff | - | 8 | 8 | 0 | 14 | 1.000 | 0.364 | 0.533 | 0 | 0.10 | 0 | - |
| statis gabungan | - | 10 | 9 | 1 | 13 | 0.900 | 0.409 | 0.563 | 0 | 2.64 | 0 | - |
| LLM single | 1 | 76 | 22 | 54 | 0 | 0.289 | 1.000 | 0.449 | 6 | 77.5 | 0.148 | 1.00 |
| LLM single | 2 | 66 | 22 | 44 | 0 | 0.333 | 1.000 | 0.500 | 5 | 73.1 | 0.140 | 1.00 |
| LLM single | 3 | 72 | 22 | 50 | 0 | 0.306 | 1.000 | 0.468 | 7 | 73.0 | 0.143 | 1.00 |
| LLM agent | 1 | 52 | 22 | 30 | 0 | 0.423 | 1.000 | 0.595 | 6 | 107.0 | 4.670 | 3.14 |
| LLM agent | 2 | 49 | 22 | 27 | 0 | 0.449 | 1.000 | 0.620 | 5 | 103.1 | 3.923 | 3.14 |
| LLM agent | 3 | 57 | 22 | 35 | 0 | 0.386 | 1.000 | 0.557 | 7 | 97.5 | 3.716 | 3.00 |

## Tabel 2. Rata-rata ± simpangan baku (hanya run lengkap)

| Kondisi | Run lengkap | Temuan | Precision | Recall | F1 | FP file bersih | Waktu/run (s) | Biaya/run (USD) | Turn/file |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LLM single | 3 | 71.3 | 0.309 ± 0.022 | 1.000 ± 0.000 | 0.472 ± 0.026 | 6.0 | 74.5 | 0.144 | 1.00 |
| LLM agent | 3 | 52.7 | 0.419 ± 0.032 | 1.000 ± 0.000 | 0.590 ± 0.032 | 6.0 | 102.5 | 4.103 | 3.10 |

## Tabel 3. Ablasi pasca-eksperimen (rata-rata run lengkap)

| Kondisi | Varian | Temuan | Precision | Recall | F1 | FP file bersih |
|---|---|---:|---:|---:|---:|---:|
| LLM single | severity high+medium | 52.7 | 0.418 ± 0.016 | 1.000 ± 0.000 | 0.590 ± 0.016 | 4.3 |
| LLM single | severity high saja | 24.0 | 0.764 ± 0.024 | 0.833 ± 0.026 | 0.797 ± 0.025 | 0.3 |
| LLM single | konsensus >= 2 dari 3 run | 74 | 0.297 | 1.000 | 0.458 | 6 |
| LLM agent | severity high+medium | 37.3 | 0.581 ± 0.018 | 0.985 ± 0.026 | 0.730 ± 0.008 | 3.7 |
| LLM agent | severity high saja | 17.3 | 0.868 ± 0.061 | 0.682 ± 0.045 | 0.763 ± 0.039 | 0.0 |
| LLM agent | konsensus >= 2 dari 3 run | 52 | 0.423 | 1.000 | 0.595 | 6 |

## Tabel 4. Recall per kategori cacat

| Kategori | pylint | bandit | ruff | statis gabungan | single r1 | single r2 | single r3 | agent r1 | agent r2 | agent r3 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| concurrency | 0/1 | 0/1 | 0/1 | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| error-handling | 1/2 | 0/2 | 0/2 | 1/2 | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| logic | 1/7 | 0/7 | 1/7 | 1/7 | 7/7 | 7/7 | 7/7 | 7/7 | 7/7 | 7/7 |
| performance | 0/1 | 0/1 | 0/1 | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| resource | 1/3 | 1/3 | 1/3 | 1/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| security | 0/8 | 6/8 | 6/8 | 6/8 | 8/8 | 8/8 | 8/8 | 8/8 | 8/8 | 8/8 |

## Tabel 5. Matriks deteksi per cacat (Y = terdeteksi)

| ID | File | Baris | Kategori | Deskripsi | pylint | bandit | ruff | statis gabungan | single r1 | single r2 | single r3 | agent r1 | agent r2 | agent r3 |
|---|---|---:|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| D01 | inventory.py | 8 | logic | Mutable default argument: list tags dipakai bersama antar pemanggilan | Y | . | Y | Y | Y | Y | Y | Y | Y | Y |
| D02 | inventory.py | 20 | logic | Off-by-one: item terakhir tidak ikut dijumlahkan | . | . | . | . | Y | Y | Y | Y | Y | Y |
| D03 | user_repo.py | 10 | security | SQL injection melalui f-string | . | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| D04 | user_repo.py | 8 | resource | Koneksi database tidak pernah ditutup | . | . | . | . | Y | Y | Y | Y | Y | Y |
| D05 | auth.py | 5 | security | Secret key di-hardcode di source code | . | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| D06 | auth.py | 9 | security | MD5 tanpa salt untuk hashing password | . | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| D07 | auth.py | 22 | security | Perbandingan token tidak constant-time (timing attack) | . | . | . | . | Y | Y | Y | Y | Y | Y |
| D08 | file_utils.py | 8 | security | Path traversal: filename tidak divalidasi | . | . | . | . | Y | Y | Y | Y | Y | Y |
| D09 | file_utils.py | 14 | security | Command injection melalui os.system | . | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| D10 | discount.py | 12 | logic | Harus >= 100 sesuai docstring | . | . | . | . | Y | Y | Y | Y | Y | Y |
| D11 | discount.py | 14 | logic | Harga akhir bisa negatif, tidak di-clamp ke 0 | . | . | . | . | Y | Y | Y | Y | Y | Y |
| D12 | cache.py | 19 | concurrency | get_or_compute tidak memakai lock (race condition) | . | . | . | . | Y | Y | Y | Y | Y | Y |
| D13 | order_parser.py | 9 | error-handling | Bare except menelan semua error | Y | . | . | Y | Y | Y | Y | Y | Y | Y |
| D14 | order_parser.py | 15 | error-handling | order bisa None, akses subscript gagal | . | . | . | . | Y | Y | Y | Y | Y | Y |
| D15 | stats.py | 5 | logic | ZeroDivisionError untuk list kosong | . | . | . | . | Y | Y | Y | Y | Y | Y |
| D16 | stats.py | 11 | logic | Median salah untuk jumlah data genap | . | . | . | . | Y | Y | Y | Y | Y | Y |
| D17 | session_store.py | 11 | security | Deserialisasi pickle dari cookie yang tidak tepercaya (RCE) | . | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| D18 | report.py | 7 | performance | Pencarian di list membuat O(n^2); seharusnya set | . | . | . | . | Y | Y | Y | Y | Y | Y |
| D19 | report.py | 21 | resource | File tidak ditutup | . | . | . | . | Y | Y | Y | Y | Y | Y |
| D20 | api_client.py | 11 | security | Verifikasi TLS dimatikan | . | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| D21 | api_client.py | 8 | resource | Request tanpa timeout | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| D22 | date_utils.py | 5 | logic | Aturan tahun kabisat salah (abad 100/400) | . | . | . | . | Y | Y | Y | Y | Y | Y |

## Tabel 6. Log eksekusi LLM per file (turn / durasi / biaya / jumlah temuan)

### Kondisi single

| File | Run 1 | Run 2 | Run 3 |
| --- | --- | --- | --- |
| `api_client.py` | 1 turn / 6.7 s / $0.017 / 9 | 1 turn / 5.7 s / $0.015 / 7 | 1 turn / 6.9 s / $0.017 / 9 |
| `auth.py` | 1 turn / 4.9 s / $0.014 / 6 | 1 turn / 5.8 s / $0.015 / 6 | 1 turn / 5.0 s / $0.015 / 6 |
| `cache.py` | 1 turn / 6.5 s / $0.016 / 7 | 1 turn / 5.5 s / $0.015 / 6 | 1 turn / 6.2 s / $0.016 / 7 |
| `date_utils.py` | 1 turn / 3.7 s / $0.012 / 2 | 1 turn / 3.8 s / $0.012 / 2 | 1 turn / 3.6 s / $0.012 / 2 |
| `discount.py` | 1 turn / 4.6 s / $0.008 / 5 | 1 turn / 4.8 s / $0.008 / 5 | 1 turn / 4.8 s / $0.008 / 5 |
| `file_utils.py` | 1 turn / 5.7 s / $0.009 / 6 | 1 turn / 5.6 s / $0.009 / 6 | 1 turn / 6.0 s / $0.010 / 7 |
| `inventory.py` | 1 turn / 5.9 s / $0.009 / 7 | 1 turn / 4.5 s / $0.008 / 5 | 1 turn / 4.7 s / $0.009 / 6 |
| `money.py` *(bersih)* | 1 turn / 8.8 s / $0.013 / 3 | 1 turn / 7.9 s / $0.012 / 3 | 1 turn / 6.9 s / $0.010 / 5 |
| `order_parser.py` | 1 turn / 5.0 s / $0.008 / 5 | 1 turn / 4.8 s / $0.007 / 4 | 1 turn / 4.9 s / $0.008 / 4 |
| `report.py` | 1 turn / 6.6 s / $0.010 / 7 | 1 turn / 6.0 s / $0.009 / 5 | 1 turn / 5.6 s / $0.009 / 5 |
| `session_store.py` | 1 turn / 5.5 s / $0.009 / 6 | 1 turn / 5.5 s / $0.008 / 5 | 1 turn / 4.9 s / $0.007 / 4 |
| `stats.py` | 1 turn / 4.2 s / $0.007 / 4 | 1 turn / 4.0 s / $0.007 / 4 | 1 turn / 4.5 s / $0.007 / 4 |
| `task_queue.py` *(bersih)* | 1 turn / 4.3 s / $0.007 / 3 | 1 turn / 3.7 s / $0.006 / 2 | 1 turn / 3.9 s / $0.007 / 2 |
| `user_repo.py` | 1 turn / 5.1 s / $0.009 / 6 | 1 turn / 5.5 s / $0.009 / 6 | 1 turn / 5.1 s / $0.009 / 6 |
| **Total** | **77.5 s / $0.148 / 76** | **73.1 s / $0.140 / 66** | **73.0 s / $0.143 / 72** |

### Kondisi agent

| File | Run 1 | Run 2 | Run 3 |
| --- | --- | --- | --- |
| `api_client.py` | 3 turn / 6.5 s / $0.419 / 3 | 3 turn / 6.8 s / $0.420 / 4 | 3 turn / 6.3 s / $0.035 / 4 |
| `auth.py` | 3 turn / 6.6 s / $0.029 / 4 | 3 turn / 7.4 s / $0.422 / 5 | 3 turn / 7.2 s / $0.416 / 6 |
| `cache.py` | 4 turn / 8.7 s / $0.970 / 5 | 3 turn / 8.0 s / $0.416 / 5 | 3 turn / 7.2 s / $0.416 / 5 |
| `date_utils.py` | 3 turn / 5.9 s / $0.412 / 2 | 3 turn / 5.8 s / $0.027 / 2 | 3 turn / 6.3 s / $0.621 / 2 |
| `discount.py` | 3 turn / 7.0 s / $0.415 / 4 | 3 turn / 6.4 s / $0.029 / 3 | 3 turn / 7.0 s / $0.416 / 6 |
| `file_utils.py` | 3 turn / 7.1 s / $0.029 / 4 | 3 turn / 5.9 s / $0.028 / 3 | 3 turn / 6.0 s / $0.028 / 3 |
| `inventory.py` | 3 turn / 7.0 s / $0.029 / 5 | 3 turn / 6.9 s / $0.415 / 4 | 3 turn / 6.4 s / $0.415 / 4 |
| `money.py` *(bersih)* | 4 turn / 13.6 s / $0.648 / 3 | 4 turn / 11.1 s / $0.645 / 2 | 3 turn / 11.0 s / $0.421 / 4 |
| `order_parser.py` | 3 turn / 7.0 s / $0.415 / 3 | 3 turn / 6.4 s / $0.028 / 3 | 3 turn / 6.2 s / $0.029 / 3 |
| `report.py` | 3 turn / 9.4 s / $0.418 / 6 | 4 turn / 11.6 s / $0.975 / 4 | 3 turn / 8.4 s / $0.418 / 6 |
| `session_store.py` | 3 turn / 6.5 s / $0.028 / 4 | 3 turn / 6.4 s / $0.028 / 4 | 3 turn / 6.3 s / $0.028 / 4 |
| `stats.py` | 3 turn / 7.1 s / $0.415 / 3 | 3 turn / 7.0 s / $0.420 / 4 | 3 turn / 6.3 s / $0.414 / 3 |
| `task_queue.py` *(bersih)* | 3 turn / 8.3 s / $0.416 / 3 | 3 turn / 7.1 s / $0.036 / 3 | 3 turn / 6.6 s / $0.029 / 3 |
| `user_repo.py` | 3 turn / 6.3 s / $0.029 / 3 | 3 turn / 6.3 s / $0.035 / 3 | 3 turn / 6.3 s / $0.030 / 4 |
| **Total** | **107.0 s / $4.670 / 52** | **103.1 s / $3.923 / 49** | **97.5 s / $3.716 / 57** |

## Contoh kualitatif

**TP semantik yang dilewatkan semua alat statis**
- `discount.py:12` (D10), agent: *"The docstring says orders of 100 or more get the 10% discount, but `total > 100` excludes exactly 100, so an order of 100 pays full price instead of 90."*
- `cache.py:19` (D12), agent: *"get_or_compute reads and writes self._data without holding self._lock, even though the class is documented as thread-safe..."*
- `inventory.py:20` (D02), single-shot: *"range(len(names) - 1) skips the last item, so total_stock under-counts the inventory (and returns 0 for a single item)."*

**FP di file bersih (agent run 1): sebagian besar saran pengerasan yang wajar**
- `money.py:6` (medium): digit desimal ketiga dipotong diam-diam, `to_cents('1.005')` → 100.
- `money.py:8` (medium): input seperti `'1.-5'` diterima karena `int()` menerima tanda.
- `task_queue.py:17` (medium): `put()` menunggu tanpa timeout atau mekanisme shutdown.
- `task_queue.py:19` (low): `notify_all()` membangunkan semua thread (thundering herd).

**Sebaran severity FP (total 3 run)**

| Kondisi | High | Medium | Low | Total FP |
| --- | ---: | ---: | ---: | ---: |
| LLM single-shot | 17 | 75 | 56 | 148 |
| Code review agent | 7 | 40 | 45 | 92 |
