# 02 — Spesifikasi Dataset `shopapp` dan *Ground Truth*

Dataset eksperimen berada di [eksperimen/dataset/shopapp/](../eksperimen/dataset/shopapp/) dengan definisi cacat di [eksperimen/ground_truth.json](../eksperimen/ground_truth.json). Dataset terdiri atas **14 berkas Python (290 baris total)** yang menyimulasikan modul backend aplikasi toko daring (*e-commerce*).

---

## 1. Ringkasan Berkas Dataset (`shopapp`)

| Berkas | Baris | Peran Modul | Cacat Tertanam | Status Kontrol |
| --- | ---: | --- | --- | --- |
| `api_client.py` | 20 | Klien HTTP untuk *payment gateway* (`charge`, `refund`) | `D20`, `D21` | Bercacat |
| `auth.py` | 22 | Hashing kata sandi & penandatanganan token HMAC | `D05`, `D06`, `D07` | Bercacat |
| `cache.py` | 26 | Cache *in-memory thread-safe* dengan penghitung *hit* | `D12` | Bercacat |
| `date_utils.py` | 13 | Helper tahun kabisat & jumlah hari per bulan | `D22` | Bercacat |
| `discount.py` | 23 | Kalkulasi diskon pesanan, kupon, dan ongkos kirim | `D10`, `D11` | Bercacat |
| `file_utils.py` | 18 | Utilitas pembacaan & kompresi unggahan admin | `D08`, `D09` | Bercacat |
| `inventory.py` | 25 | Manajemen stok barang (`Inventory`) | `D01`, `D02` | Bercacat |
| `money.py` | 21 | Konversi sen integer, pemformatan, dan pembagian rata | — | **Kontrol Bersih** |
| `order_parser.py` | 15 | Parser payload JSON pesanan masuk | `D13`, `D14` | Bercacat |
| `report.py` | 23 | Laporan penjualan harian & daftar pelanggan unik | `D18`, `D19` | Bercacat |
| `session_store.py` | 16 | Serialisasi sesi pengguna pada cookie | `D17` | Bercacat |
| `stats.py` | 17 | Statistik penjualan (`average`, `median`, `growth_rate`) | `D15`, `D16` | Bercacat |
| `task_queue.py` | 27 | Antrean FIFO terbatas berbasis `threading.Condition` | — | **Kontrol Bersih** |
| `user_repo.py` | 24 | Lapisan akses data pengguna berbasis SQLite | `D03`, `D04` | Bercacat |
| **Total (14 berkas)** | **290** | — | **22 cacat** | **12 bercacat, 2 bersih** |

---

## 2. Daftar Lengkap 22 Cacat Tertanam (*Ground Truth*)

Setiap nomor baris (`Baris`) di bawah diresolusi otomatis oleh `common.ground_truth()` melalui pencocokan string `anchor`.

| ID | Berkas | Baris | Kategori | Anchor Kode | Deskripsi Cacat & Dampak Kegagalan |
| --- | --- | ---: | --- | --- | --- |
| `D01` | `inventory.py` | 8 | `logic` | `tags=[]` | *Mutable default argument*: list `tags` dipakai bersama lintas pemanggilan `add_item()`. |
| `D02` | `inventory.py` | 20 | `logic` | `range(len(names) - 1)` | *Off-by-one*: elemen terakhir `names` tidak pernah dijumlahkan dalam `total_stock()`. |
| `D03` | `user_repo.py` | 10 | `security` | `f"SELECT id` | SQL injection melalui interpolasi *f-string* langsung pada query `username`. |
| `D04` | `user_repo.py` | 8 | `resource` | `conn = sqlite3.connect(DB_PATH)` | Koneksi SQLite pada `find_user_by_name()` dibuka tanpa `close()` / context manager penutup. |
| `D05` | `auth.py` | 5 | `security` | `SECRET_KEY = ` | Kunci rahasia live (`sk_live_...`) di-*hardcode* langsung di dalam kode sumber. |
| `D06` | `auth.py` | 9 | `security` | `hashlib.md5` | Hashing kata sandi memakai MD5 tanpa *salt* (rentan *brute-force* dan *rainbow table*). |
| `D07` | `auth.py` | 22 | `security` | `return expected == token` | Verifikasi tanda tangan token menggunakan `==` biasa, tidak *constant-time* (rentan *timing attack*). |
| `D08` | `file_utils.py` | 8 | `security` | `path = os.path.join(UPLOAD_DIR, filename)` | *Path traversal*: `filename` tidak divalidasi sehingga `../` atau path absolut dapat membaca berkas sembarang. |
| `D09` | `file_utils.py` | 14 | `security` | `os.system(` | *Command injection* melalui `os.system("gzip -k " + ...)` pada input `filename`. |
| `D10` | `discount.py` | 12 | `logic` | `if total > 100:` | Pelanggaran kontrak docstring: seharusnya `>= 100` (*"Orders of 100 or more get a 10% discount"*). |
| `D11` | `discount.py` | 14 | `logic` | `total = total - coupon_value` | Pelanggaran kontrak docstring: hasil pengurangan kupon tidak di-*clamp* ke `0` sehingga harga akhir bisa negatif. |
| `D12` | `cache.py` | 19 | `concurrency` | `if key not in self._data:` | `get_or_compute()` membaca dan menulis `self._data` tanpa memegang `self._lock` (*race condition*). |
| `D13` | `order_parser.py` | 9 | `error-handling` | `except:` | *Bare except* menelan semua pengecualian (termasuk `KeyboardInterrupt`/`SystemExit` dan bug tak terduga). |
| `D14` | `order_parser.py` | 15 | `error-handling` | `return len(order["items"])` | `parse_order(raw)` dapat mengembalikan `None`, sehingga `order["items"]` memicu `TypeError`. |
| `D15` | `stats.py` | 5 | `logic` | `return sum(values) / len(values)` | `ZeroDivisionError` ketika `average([])` dipanggil dengan list kosong. |
| `D16` | `stats.py` | 11 | `logic` | `return s[mid]` | Perhitungan median salah untuk panjang data genap (hanya mengambil indeks tengah atas, bukan rata-rata dua nilai tengah). |
| `D17` | `session_store.py` | 11 | `security` | `pickle.loads(` | Deserialisasi `pickle` terhadap nilai cookie dari klien yang tidak tepercaya memungkinkan *Remote Code Execution* (RCE). |
| `D18` | `report.py` | 7 | `performance` | `not in seen:` | Pencarian keanggotaan pada `list` `seen` menghasilkan kompleksitas waktu $O(n^2)$; seharusnya memakai `set`. |
| `D19` | `report.py` | 21 | `resource` | `f = open(path, "w")` | Pegangan berkas dibuka di `write_report()` tanpa pernah ditutup (`with open(...)`). |
| `D20` | `api_client.py` | 11 | `security` | `verify=False` | Menonaktifkan verifikasi sertifikat TLS pada transaksi pembayaran `charge()`. |
| `D21` | `api_client.py` | 8 | `resource` | `resp = requests.post(` | Panggilan `requests.post` di `charge()` tidak menyertakan parameter `timeout` (berbeda dengan `refund()` yang memakai `timeout=10`). |
| `D22` | `date_utils.py` | 5 | `logic` | `return year % 4 == 0` | Aturan tahun kabisat tidak lengkap: mengabaikan pengecualian abad 100 dan kelipatan 400 (mis. `1900` dianggap kabisat). |

---

## 3. Distribusi Kategori & Berkas Kontrol Bersih

### Distribusi Kategori Cacat

| Kategori | Jumlah Cacat | Persentase | ID Cacat |
| --- | ---: | ---: | --- |
| `security` | 8 | 36,4% | `D03`, `D05`, `D06`, `D07`, `D08`, `D09`, `D17`, `D20` |
| `logic` | 7 | 31,8% | `D01`, `D02`, `D10`, `D11`, `D15`, `D16`, `D22` |
| `resource` | 3 | 13,6% | `D04`, `D19`, `D21` |
| `error-handling` | 2 | 9,1% | `D13`, `D14` |
| `concurrency` | 1 | 4,5% | `D12` |
| `performance` | 1 | 4,5% | `D18` |
| **Total** | **22** | **100,0%** | — |

### Berkas Kontrol Negatif (Tanpa Cacat Tertanam)

1. **`money.py` (21 baris):** Implementasi `to_cents(amount_str)`, `format_cents(cents)`, dan `split_evenly(cents, parts)` dengan validasi `parts <= 0` serta aritmetika integer sen untuk menghindari galat *floating-point*.
2. **`task_queue.py` (27 baris):** Implementasi `TaskQueue(maxsize)` dengan validasi `maxsize <= 0`, `collections.deque()`, serta sinkronisasi `threading.Condition()` yang menjaga invarian batas penuh (`while len >= maxsize`) dan kosong (`while not items`).

Setiap temuan yang dilaporkan alat maupun LLM pada dua berkas ini dihitung langsung sebagai `CleanFP` (*Clean-File False Positive*).
