# Ringkasan Hasil Evaluasi (dibuat otomatis oleh evaluate.py)

Dataset: 14 file, 22 cacat ground truth, 2 file bersih (kontrol negatif).

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
