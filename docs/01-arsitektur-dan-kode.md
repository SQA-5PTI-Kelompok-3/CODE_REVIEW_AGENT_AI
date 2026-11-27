# 01 — Arsitektur dan Dokumentasi Kode Eksperimen

Dokumen ini menjelaskan arsitektur teknis, rancangan isolasi eksperimen, antarmuka modul Python, desain prompt, dan skema keluaran JSON pada direktori [eksperimen/](../eksperimen/).

---

## 1. Desain Kontrol & Isolasi Eksperimen

Untuk menjaga validitas internal perbandingan antara **LLM Single-Shot** dan **Code Review Agent**, eksperimen menerapkan tiga kontrol utama:

1. **Isolasi Direktori dari *Ground Truth*:**
   Skrip `run_llm.py` menyalin `eksperimen/dataset/shopapp/` ke direktori sementara `tempfile.mkdtemp(prefix="crx_") / "shopapp"` sebelum menjalankan `claude -p`. Dengan demikian, *Code Review Agent* yang memiliki akses alat `Read`, `Grep`, dan `Glob` tidak dapat keluar ke direktori induk untuk membaca `ground_truth.json`, `evaluate.py`, maupun `results/`.
2. **Keseragaman Model dan Format Keluaran:**
   Kedua kondisi menggunakan model yang sama (`sonnet` pada Claude Code headless `claude -p --output-format json --no-session-persistence`) serta format keluaran JSON array seragam dengan skema:
   ```json
   [
     {
       "line": 11,
       "category": "security|logic|resource|concurrency|error-handling|performance|other",
       "severity": "high|medium|low",
       "message": "Satu kalimat penjelasan skenario kegagalan."
     }
   ]
   ```
3. **Kontrol Negatif (*Decoy Clean Files*):**
   Dua berkas (`money.py` dan `task_queue.py`) sengaja dibuat bersih tanpa cacat tertanam (`0` entri pada `ground_truth.json`) untuk mengukur kecenderungan *over-reporting* (`CleanFP`).

---

## 2. Dokumentasi Modul Python

### 2.1 `eksperimen/common.py`

Modul utilitas bersama yang menyediakan konfigurasi jalur, resolusi *ground truth*, dan algoritma pencocokan temuan.

| Simbol / Fungsi | Tipe / Signature | Deskripsi |
| --- | --- | --- |
| `ROOT` | `Path` | Direktori induk `eksperimen/`. |
| `DATASET` | `Path` | Menunjuk ke `eksperimen/dataset/shopapp`. |
| `RESULTS` | `Path` | Menunjuk ke `eksperimen/results`. |
| `TOLERANCE` | `int = 2` | Toleransi selisih nomor baris (`\|line - line_gt\| <= 2`) agar temuan dianggap cocok dengan cacat *ground truth*. |
| `files()` | `() -> list[str]` | Mengembalikan daftar nama berkas `*.py` terurut alfabetis di `DATASET`. |
| `ground_truth()` | `() -> list[dict]` | Memuat `ground_truth.json`, mencari nomor baris aktual pertama yang mengandung substring `anchor` pada berkas terkait (`assert hits`), lalu menyisipkan kunci `"line"`. |
| `match(findings, gt)` | `(list[dict], list[dict]) -> tuple[list, list, list]` | Pencocokan *greedy* satu-ke-satu (mengurutkan seluruh pasangan `(abs(line - g["line"]), fi, gi)` dengan berkas sama dan jarak $\le$ `TOLERANCE`, memilih jarak terdekat tanpa duplikasi). Mengembalikan `(tp, fp, fn)`. |

---

### 2.2 `eksperimen/run_static.py`

Menjalankan tiga alat analisis statis lokal secara berurutan terhadap seluruh 14 berkas di `DATASET` dan menyimpan keluaran terstandarisasi ke `results/static_<tool>.json`.

| Fungsi | Perintah yang Dijalankan | Pemetaan Output |
| --- | --- | --- |
| `run(cmd)` | `subprocess.run(cmd, capture_output=True, text=True)` | Mengembalikan `(stdout, durasi_detik)` memakai `time.perf_counter()`. |
| `pylint()` | `python -m pylint --output-format=json --disable=C,R <paths>` | Mengambil `path`, `line`, `message-id + symbol`, `message`. Flag `--disable=C,R` menonaktifkan pesan gaya (*Convention*) dan refaktor (*Refactor*). |
| `bandit()` | `python -m bandit -f json -q <paths>` | Mengambil `filename`, `line_number`, `test_id`, `issue_text`. |
| `ruff()` | `python -m ruff check --select F,B,S --output-format json --no-cache <paths>` | Memilih kategori `F` (Pyflakes), `B` (flake8-bugbear), dan `S` (flake8-bandit). |

**Skema keluaran `results/static_<tool>.json`:**

```json
{
  "tool": "ruff",
  "seconds": 0.1,
  "findings": [
    {
      "file": "api_client.py",
      "line": 8,
      "rule": "S113",
      "message": "Probable use of `requests` call without timeout"
    }
  ]
}
```

---

### 2.3 `eksperimen/run_llm.py`

Menjalankan eksperimen komparatif kondisi `single` dan `agent` melalui Claude Code CLI (`claude -p`).

**Pemakaian:**

```bash
python eksperimen/run_llm.py <run_id> [model]
# Default: run_id="1", model="sonnet"
```

**Detail Implementasi:**

| Fungsi | Deskripsi |
| --- | --- |
| `build(cond, f)` | Untuk `cond == "single"`, membaca isi berkas `f`, memberi nomor baris (`f"{i + 1:3d}  {ln}"`), memformat `prompts/single_shot.txt`, dan menambahkan argumen `["--tools", ""]`. Untuk `cond == "agent"`, hanya mengirim nama berkas `f` ke `prompts/agent.txt` dengan argumen `["--tools", "Read,Grep,Glob", "--allowedTools", "Read,Grep,Glob"]`. |
| `parse(text)` | Mengekstrak array JSON pertama melalui `re.search(r"\[.*\]", text, re.S)` dan mengembalikan `[]` bila parsing gagal (`json.JSONDecodeError`). |
| `review(job)` | Menjalankan `claude -p --output-format json --model <MODEL> --no-session-persistence` di direktori `WORKDIR` (`crx_*/shopapp`) dengan `timeout=900` detik, lalu merekam `seconds`, `num_turns`, `total_cost_usd`, `raw`, dan `findings`. |
| Eksekutor Paralel | Menjalankan 28 pekerjaan (`2 kondisi × 14 berkas`) menggunakan `ThreadPoolExecutor(max_workers=4)` dan menulis hasil ke `results/llm_single_run<RUN>.json` serta `results/llm_agent_run<RUN>.json`. |
| `failed(r)` dan `--retry-failed` | `failed()` menandai review yang gagal (temuan kosong dan pesan limit, atau biaya 0). Dengan `--retry-failed`, hanya review gagal pada run tersebut yang dijalankan ulang, lalu hasilnya digabung ke JSON lama tanpa mengubah review yang sudah berhasil. |

**Skema keluaran `results/llm_<cond>_run<RUN>.json`:**

```json
{
  "cond": "agent",
  "run": "1",
  "model": "sonnet",
  "reviews": [
    {
      "cond": "agent",
      "file": "api_client.py",
      "seconds": 6.5,
      "num_turns": 3,
      "cost_usd": 0.4192183,
      "raw": "[...]",
      "findings": [
        {
          "line": 11,
          "category": "security",
          "severity": "high",
          "message": "...",
          "file": "api_client.py"
        }
      ]
    }
  ]
}
```

---

### 2.4 `eksperimen/evaluate.py`

Menghitung semua metrik dan mencetak lima tabel: hasil per metode dan run, rata-rata ± simpangan baku run lengkap, ablasi pasca-eksperimen, recall per kategori, dan matriks deteksi per cacat. `python evaluate.py --md results/summary.md` juga menulis tabel-tabel itu ke Markdown.

| Simbol / fungsi | Deskripsi |
| --- | --- |
| `SEMANTIC_MISMATCH` | Pasangan `(tool, rule)` yang barisnya kebetulan cocok dengan cacat tetapi isinya membahas hal lain. Saat ini hanya `("pylint", "W1514")`; temuan seperti ini dihitung FP. |
| `metrics(findings, gt=None)` | Menghitung `tp`, `fp`, `fn`, precision, recall, F1, `clean_fp` (FP di `money.py` dan `task_queue.py`), daftar cacat yang ditemukan dan terlewat. |
| `is_failed(review)` | Menandai review yang gagal (temuan kosong dan pesan limit, atau biaya 0). Review gagal tidak dihitung; run yang memuatnya ditandai "tidak lengkap". |
| `load_static(tool)`, `load_static_union()` | Memuat hasil satu alat statis, atau gabungan ketiganya (deduplikasi per `(file, baris)`). |
| `load_llm(cond, run, severities=None)` | Memuat satu run LLM; opsi filter severity untuk ablasi. |
| `majority(run_findings, k=2)` | Konsensus: temuan run pertama yang juga muncul (file sama, baris ±2) di minimal `k` run. |
| `category_recall(matched)` | Jumlah cacat terdeteksi per kategori. |

---

## 3. Desain & Teks Prompt Lengkap (`eksperimen/prompts/`)

### 3.1 Prompt Single-Shot (`single_shot.txt`)

- **Peran:** *"You are a senior Python code reviewer."*
- **Input:** Nama berkas dan seluruh kode sumber bernomor baris ditempel langsung ke prompt.
- **Instruksi:** Cari *real defects* (bug, logika, keamanan, kebocoran sumber daya, konkurensi, penanganan error, performa); abaikan gaya penulisan semata; keluarkan hanya array JSON.

````text
You are a senior Python code reviewer. Review the file below for real defects:
bugs, logic errors, security vulnerabilities, resource leaks, concurrency problems,
error-handling problems and significant performance problems. Ignore pure style.

File: {file}
```python
{numbered_code}
```

Respond with ONLY a JSON array (no prose, no code fence). Each element:
{{"line": <int line number>, "category": "security|logic|resource|concurrency|error-handling|performance|other",
  "severity": "high|medium|low", "message": "<one sentence>"}}
Return [] if there are no defects.
````

### 3.2 Prompt Code Review Agent (`agent.txt`)

- **Peran:** *"You are a code review agent for the Python project in the current directory."*
- **Input:** Hanya nama berkas `{file}` (kode tidak ditempel).
- **Alur 4 Langkah:**
  1. Baca `{file}` menggunakan `Read`.
  2. Investigasi konteks lintas berkas menggunakan `Grep`/`Glob`/`Read` untuk memeriksa cara fungsi dipakai di proyek maupun *docstring*/kontrak.
  3. Periksa terhadap daftar periksa terstruktur (kebenaran vs spesifikasi, *edge case*, keamanan, manajemen sumber daya, konkurensi, penanganan error, performa).
  4. **Self-verification:** Baca ulang baris kandidat temuan dan buang jika tidak dapat menjelaskan skenario kegagalan konkret.

```text
You are a code review agent for the Python project in the current directory.
Your task: review the file `{file}` for real defects.

Work in steps:
1. Read `{file}` with the Read tool.
2. Investigate context: use Grep/Glob/Read to look at how its functions are used
   elsewhere in the project and at any docstrings/contracts that define expected behaviour.
3. Check against this checklist: correctness vs. documented behaviour, edge cases
   (empty input, zero, None, boundaries), security (injection, secrets, crypto,
   deserialization, path traversal, TLS), resource handling (files, connections,
   timeouts), concurrency (shared state without locks), error handling, performance.
4. Self-verify: for each candidate finding, re-read the exact line and drop it if you
   cannot explain a concrete failure scenario. Ignore pure style.

Final answer: ONLY a JSON array (no prose, no code fence) of findings located in `{file}`. Each element:
{{"line": <int line number in {file}>, "category": "security|logic|resource|concurrency|error-handling|performance|other",
  "severity": "high|medium|low", "message": "<one sentence with the failure scenario>"}}
Return [] if there are no defects.
```
