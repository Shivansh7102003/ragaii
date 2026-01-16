# 🌐 Website Q&A RAG System

A powerful Retrieval-Augmented Generation (RAG) system that allows you to index any website and ask questions about its content using natural language. Built with Streamlit, LangChain, and Groq.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

- 🌐 **Website Crawling**: Automatically crawl and index entire websites
- 💾 **Smart Caching**: FAISS-based vector storage with intelligent caching
- 🤖 **Multiple LLM Models**: Support for latest Groq models including Llama 3.3 and GPT-OSS
- 💬 **Conversational Interface**: Chat-based Q&A with context-aware responses
- 🔍 **Relevance Checking**: Validates if answers are grounded in the indexed content
- ⚡ **Fast Retrieval**: Efficient similarity search using FAISS vector database

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Groq API key ([Get one here](https://console.groq.com/))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/website-qa-rag.git
   cd website-qa-rag
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   .\venv\Scripts\Activate.ps1
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your Groq API key
   # API_KEY=your_groq_api_key_here
   ```

### Running the Application

```bash
streamlit run streamlit.py
```

The application will open in your browser at `http://localhost:8501`

## 📖 Usage

1. **Enter a Website URL**: Paste any website URL in the sidebar
2. **Index the Website**: Click "🔍 Index Website" to crawl and process the content
3. **Select a Model**: Choose from available Groq models
4. **Ask Questions**: Start chatting about the website content!

### Supported Models

- `llama-3.1-8b-instant` - Fast and efficient
- `llama-3.3-70b-versatile` - More powerful reasoning
- `meta-llama/llama-4-maverick-17b-128e-instruct` - Latest Llama 4
- `openai/gpt-oss-safeguard-20b` - GPT-based open source

## 🏗️ Project Structure

```
website-qa-rag/
├── streamlit.py              # Main Streamlit UI
├── app.py                    # Core RAG logic
├── webcrawler/               # Website crawling module
│   ├── __init__.py
│   ├── crawler.py           # Web scraping logic
│   └── text_processor.py   # Text processing utilities
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `API_KEY` | Your Groq API key | Yes |

### Customization

You can customize the RAG parameters in `app.py`:

```python
DEFAULT_CHUNK_SIZE = 1000      # Text chunk size
DEFAULT_CHUNK_OVERLAP = 100    # Overlap between chunks
DEFAULT_K_VALUE = 5            # Number of chunks to retrieve
DEFAULT_TEMPERATURE = 0.5      # LLM temperature
DEFAULT_MAX_TOKENS = 500       # Max response length
```

## 🛠️ Technologies Used

- **[Streamlit](https://streamlit.io/)** - Web interface
- **[LangChain](https://langchain.com/)** - LLM framework
- **[Groq](https://groq.com/)** - LLM inference
- **[FAISS](https://github.com/facebookresearch/faiss)** - Vector similarity search
- **[HuggingFace](https://huggingface.co/)** - Embeddings (sentence-transformers)
- **[Trafilatura](https://trafilatura.readthedocs.io/)** - Web content extraction
- **[BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)** - HTML parsing

## 📝 How It Works

1. **Website Crawling**: The system crawls the provided URL and extracts clean text content
2. **Text Chunking**: Content is split into manageable chunks with overlap
3. **Embedding**: Each chunk is converted to vector embeddings using HuggingFace models
4. **Vector Storage**: Embeddings are stored in FAISS for fast similarity search
5. **Query Processing**: User questions are embedded and matched against stored chunks
6. **Response Generation**: Relevant chunks are sent to the LLM to generate accurate answers
7. **Validation**: Responses are validated to ensure they're grounded in the indexed content

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is for educational and research purposes. Please respect website terms of service and robots.txt when crawling websites.

## 🙏 Acknowledgments

- Built with [LangChain](https://langchain.com/)
- Powered by [Groq](https://groq.com/)
- UI by [Streamlit](https://streamlit.io/)

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Made with ❤️ using LangChain and Groq**
