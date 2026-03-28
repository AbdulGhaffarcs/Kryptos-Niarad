<div align="center">

<img src="./banner.svg" width="100%" alt="NIARAD"/>

<br/>

![Status](https://img.shields.io/badge/Status-Active_Development-000000?style=flat-square&logoColor=FFC800&labelColor=060910&color=00FFAA)
![Version](https://img.shields.io/badge/Version-2.1_Cloud-000000?style=flat-square&labelColor=060910&color=00C8FF)
![Python](https://img.shields.io/badge/Python-3.10+-000000?style=flat-square&logo=python&logoColor=00FFAA&labelColor=060910&color=1C2A3A)
![Streamlit](https://img.shields.io/badge/Streamlit-App-000000?style=flat-square&logo=streamlit&logoColor=00FFAA&labelColor=060910&color=1C2A3A)
![Inference](https://img.shields.io/badge/Inference-Cloud_LPU-000000?style=flat-square&logoColor=00FFAA&labelColor=060910&color=1C2A3A)
![FAISS](https://img.shields.io/badge/FAISS-Vector_Store-000000?style=flat-square&logoColor=00FFAA&labelColor=060910&color=1C2A3A)
![LangChain](https://img.shields.io/badge/LangChain-RAG-000000?style=flat-square&logoColor=00FFAA&labelColor=060910&color=1C2A3A)

<br/>

> *"Information is the resolution of uncertainty."*

</div>

---

## `// OVERVIEW`

**NIARAD** is a lightning-fast, cloud-secured AI study assistant built for students. Powered by high-speed LPU cloud inference, it delivers instant responses with nearly zero local hardware requirements. Out of the box, it answers general academic questions — and when you upload your study material, it switches into document-aware RAG mode, extracting facts, parsing schedules, and summarizing lectures in milliseconds.

```text
Low RAM requirement. Instant inference. Secure backend authorization.
```

---

## `// FEATURES`

<table>
<tr>
<td width="50%">

**`EXTRACTION MODE`**
> Pulls specific facts, dates, venues, and tables from uploaded documents. Outputs Markdown tables for schedules.

**`SYNTHESIS MODE`**
> Transforms complex lecture slides and notes into structured, bullet-pointed summaries.

**`LIGHTWEIGHT CORE`**
> Bypasses heavy local GPU requirements by routing inference through secure cloud servers.

</td>
<td width="50%">

**`HEURISTIC ROUTING`**
> Every query is automatically classified as EXTRACTION or SUMMARY via a fast keyword heuristic, saving precious LLM calls.

**`SMALL TALK DETECTION`**
> Greetings bypass the RAG vault entirely for instant, natural conversational responses.

**`PERSISTENT VAULT`**
> Documents embedded locally via FAISS persist across sessions. Upload once, query forever.

</td>
</tr>
</table>

---

## `// TECH STACK`

| Layer | Technology |
|---|---|
| 🖥 UI | Streamlit |
| 🧠 AI Engine | Cloud LPU Inference (`llama-3.1`, `mixtral`, etc.) |
| 🔢 Embeddings | HuggingFace (`all-MiniLM-L6-v2` local) |
| 🗄 Vector Store | FAISS (local disk) |
| ⛓ RAG Framework | LangChain |
| 🔐 Environment | python-dotenv |
| 📄 Document Parsing | PyMuPDF, python-pptx, openpyxl, docx2txt |

---

## `// PROJECT STRUCTURE`

```text
Local_RAG_Bot/
│
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── .env                      # Secure environment variables (Hidden)
├── .gitignore                # Security rules for version control
│
├── core/
│   ├── loaders.py            # File loading & text chunking
│   ├── vector_store.py       # Local FAISS index management & embeddings
│   └── logic_engine.py       # LLM chains & query routing
│
├── faiss_index/              # Auto-created on first document upload
│
└── .streamlit/
    └── config.toml           # Dark theme configuration
```

---

## `// INSTALLATION`

**Prerequisites**
- Python `3.10+`

<br/>

**1 — Clone Repository**
```bash
git clone [https://github.com/AbdulGhaffarcs/Kryptos-Niarad.git](https://github.com/AbdulGhaffarcs/Kryptos-Niarad.git)
cd Kryptos-Niarad
```

**2 — Install Dependencies**
```bash
pip install -r requirements.txt
```

**3 — System Authorization**
Create a file named `.env` in the root directory to hold your backend access token (obtained via Groq Console):
```env
GROQ_API_KEY=your_secure_token_here
```
> ⚠ **SECURITY NOTICE:** Ensure you have created a `.gitignore` file that includes `.env` so your authorization keys are never pushed to public repositories.

**4 — Create Theme Config**
Create `.streamlit/config.toml`:
```toml
[theme]
base = "dark"
backgroundColor = "#080B0F"
secondaryBackgroundColor = "#0D1117"
textColor = "#C8D6E5"
primaryColor = "#00FFAA"
```

**5 — Launch AI Core**
```bash
streamlit run app.py
```

---

## `// USAGE`

### Upload & Index Documents
1. Upload files via the **sidebar uploader** (PDF, DOCX, PPTX, XLSX, CSV)
2. Click **UPDATE LOCAL BRAIN** to index them into the local vector vault
3. Once the vault is online — all analytical queries run through RAG automatically

### Response Mode Badges

| Badge | Meaning |
|---|---|
| `EXTRACTION` | Pulled specific facts or tables from your indexed documents |
| `SUMMARY` | Explained a concept or summarized content from documents |
| `CHATBOT` | Answered from LLM base knowledge — no docs indexed |
| `NIARAD` | Small talk response — router bypassed for speed |
| `BLOCKED` | Query intercepted by academic safety guardrails |

---

## `// SUPPORTED FILE TYPES`

```text
  .pdf    →  PyMuPDF loader
  .docx   →  Docx2txt loader
  .pptx   →  python-pptx (slide-by-slide extraction)
  .xlsx   →  openpyxl (sheet-by-sheet extraction)
  .csv    →  built-in csv reader
```

> ⚠ Image-based / scanned PDFs won't extract text. Use OCR-processed PDFs.

---

## `// PERFORMANCE`

| Query Type | LLM Calls | Speed |
|---|---|---|
| Greeting / small talk | 1 | Lightning (~0.5s) |
| General question (no docs) | 1 | Lightning (~1s) |
| Document query (RAG) | 1 | Lightning (~1.5s) |
| Vault Synchronization | N/A | Dependent on file size (Local CPU) |

> 💡 **Hardware Impact:** Requires minimal RAM (1-2GB) to run Streamlit and the local lightweight embedding model. Can comfortably run on older hardware.

---

## `// TROUBLESHOOTING`

| Error | Fix |
|---|---|
| `ModuleNotFoundError: faiss` | Ensure you ran `pip install faiss-cpu` |
| `System Offline` | Check your `.env` file. Ensure `GROQ_API_KEY` is correct and active. |
| `No text extracted from PPTX` | Ensure file is `.pptx` not legacy `.ppt` |
| UI shows in light theme | Ensure `.streamlit/config.toml` exists with `base = "dark"` |
| `Pydantic V1` warning | Downgrade to Python 3.11 for full compatibility |

---

<div align="center">

```text
NIARAD v2.0  //  BUILT FOR STUDENTS  //  CLOUD SECURE  //  ZERO TELEMETRY  
```

</div>
