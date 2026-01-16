# Setup Guide

## First-Time Setup

Follow these steps to set up the Website Q&A RAG System on your local machine.

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/website-qa-rag.git
cd website-qa-rag
```

### 2. Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages:
- LangChain ecosystem (langchain, langchain-core, langchain-community, etc.)
- Groq API client
- FAISS for vector storage
- Streamlit for the web interface
- Web scraping tools (trafilatura, beautifulsoup4, requests)
- And more...

### 4. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Groq API key:
   ```
   API_KEY=your_actual_groq_api_key_here
   ```

3. **Get a Groq API Key:**
   - Visit [https://console.groq.com/](https://console.groq.com/)
   - Sign up or log in
   - Navigate to API Keys section
   - Create a new API key
   - Copy and paste it into your `.env` file

### 5. Run the Application

```bash
streamlit run streamlit.py
```

The application will automatically open in your default browser at `http://localhost:8501`

## Troubleshooting

### Import Errors

If you encounter module import errors, ensure all dependencies are installed:
```bash
pip install -r requirements.txt --upgrade
```

### API Key Issues

- Make sure your `.env` file is in the project root directory
- Verify the API key is valid and has not expired
- Check that the key is correctly formatted (no extra spaces or quotes)

### FAISS Index Issues

If you encounter FAISS-related errors:
```bash
# Delete the cache and re-index
rm -rf faiss_indexes/
```

Then restart the application and re-index your website.

## Development Setup

### Running Tests

```bash
# Run specific test files
python test_webcrawler.py
python test_answer_validation.py
```

### Code Structure

- `streamlit.py` - Main UI application
- `app.py` - Core RAG logic and LLM integration
- `webcrawler/` - Website crawling and processing module
  - `crawler.py` - Web scraping logic
  - `text_processor.py` - Text extraction and cleaning
  - `__init__.py` - Module initialization

## Next Steps

1. ✅ Start the application
2. ✅ Enter a website URL
3. ✅ Click "Index Website"
4. ✅ Start asking questions!

## Support

For issues or questions:
- Check the [README.md](README.md) for detailed documentation
- Open an issue on GitHub
- Review the code comments for implementation details

---

**Happy coding! 🚀**
