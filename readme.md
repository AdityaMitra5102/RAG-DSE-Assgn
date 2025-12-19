## RAG on RFCs

This is aimed to answer questions from RFCs.

Use Python 3.11 or up.

**Install Ollama:**

```bash
brew install ollama
brew services start ollama
```

Or download from https://ollama.com/download

**Install Tesseract:**

```bash
brew install tesseract
```

**Install all requirements**

```
pip install -r requirements.txt
```

or

```bash
uv sync
```

## First run will take a lot of time because it will install models, download dataset and index the metadata

**Start the application**

```bash
uv run python main.py
```

or

Start main.py
