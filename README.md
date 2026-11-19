# AI Agent for Government Scheme Eligibility and Application Verification

A Python + Streamlit web application using Retrieval-Augmented Generation (RAG), an LLM, ChromaDB, and four specialized agents.

## Features
- Upload official government scheme PDFs, TXT, or Markdown files.
- Chunk, embed, and store source content in ChromaDB.
- Retrieve relevant scheme rules before generating answers.
- Research agent: identifies potentially relevant schemes.
- Eligibility agent: compares applicant details with retrieved criteria.
- Document agent: identifies available, missing, and unclear documents.
- Guidance agent: produces source-grounded application steps.
- Source filename and page metadata are included in retrieved context.

## Technology stack
Python 3.10+, Streamlit, OpenAI chat and embedding models, LangChain, ChromaDB, PyPDF.

## Windows 11 setup (VS Code terminal / PowerShell)

1. Install Python 3.10 or newer and VS Code.
2. Extract this ZIP and open the `government_scheme_ai_agent` folder in VS Code.
3. Open Terminal -> New Terminal.
4. Create a virtual environment:

   ```powershell
   py -m venv .venv
   ```

5. Activate it:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, run this for the current terminal only, then activate again:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1
   ```

6. Install packages:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

7. Copy `.env.example` to `.env`. For Nexus, set your key and use a chat model enabled for that key. The tested configuration is:

   ```env
   NEXUS_BASE_URL=https://nexusapi.navigatelabs.ai
   NEXUS_API_KEY=your_nexus_key_here
   NEXUS_MODEL=nova-micro
   NEXUS_EMBEDDING_MODEL=text-embedding-3-small
   ```

   The app also supports OpenAI by setting `OPENAI_API_KEY`, `OPENAI_MODEL`, and `OPENAI_EMBEDDING_MODEL` instead. Nexus settings take precedence when `NEXUS_API_KEY` is present.

8. Start the app:

   ```powershell
   streamlit run app.py
   ```

9. Streamlit opens the app in your browser (usually `http://localhost:8501`).
10. In the sidebar, upload official scheme PDFs and click **Index uploaded documents**. Then use the three tabs.

## Important: official source data
The project intentionally does not invent scheme rules or include unverified eligibility criteria. Collect current documents from official government sources only, for example:
- National Government Services Portal: https://services.india.gov.in/
- myScheme: https://www.myscheme.gov.in/
- Tamil Nadu e-Governance Agency: https://tnega.tn.gov.in/

Download the scheme guidelines / official application instructions as PDF where available. Keep a record of document title, issuing department, publication/update date, and official source URL. Upload those documents into the app. Check whether each source is still current before a project demonstration.

## Agent workflow

```text
Applicant profile
      |
      v
Scheme Research Agent
      |
      v
RAG Retriever <----> ChromaDB <---- Official scheme PDFs
      |
      +--> Eligibility Agent
      |
      +--> Document Verification Agent
      |
      +--> Application Guidance Agent
      |
      v
Evidence-based result + source references
```

## Reliability and safety design
- The LLM is instructed to use retrieved context and not invent rules.
- Missing evidence is labelled unknown / insufficient information.
- Results are preliminary and must be confirmed with the department.
- Do not upload Aadhaar numbers, bank account numbers, passwords, or other unnecessary sensitive identifiers. Use minimum applicant details.
- Keep `.env` private; never commit API keys to GitHub.
- API usage may incur charges. Set provider spending limits and monitor usage.

## Current limitations / next development tasks
- Add OCR for scanned PDFs.
- Add source freshness checks and an administrator approval workflow.
- Add structured extraction of criteria into a validated database.
- Add user login, consent, secure storage, audit logs, and rate limiting before public deployment.
- Add unit/integration tests and evaluate answers against a manually verified test set.
- Add official portal links only after validating them from the source documents.
- This prototype does not submit applications or make legally binding eligibility decisions.

## Troubleshooting
- `streamlit is not recognized`: activate `.venv`, then run `python -m streamlit run app.py`.
- API authentication error: check `.env`, key validity, billing, and model access.
- No results: upload and index relevant official documents first.
- PDF parsing is poor: the PDF may be scanned; OCR support is not included in this initial version.
