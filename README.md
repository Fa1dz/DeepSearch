# 🔍 DeepSearch Advanced

## 🚧 Currently Under Construction (Adding Bypass CAPTCHA Functionality) 🚧 

**AI-Powered Web Search & Reasoning Engine**

A sophisticated Python tool that performs deep web searches with advanced analysis, credibility scoring, sentiment analysis, and semantic reasoning. Features both CLI and beautiful GUI interfaces.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)

---

## ✨ Features

### 🔎 Search Capabilities
- **Multi-source Search**: DuckDuckGo integration for ethical, privacy-respecting searches
- **Smart Crawling**: Respects `robots.txt` and implements polite rate limiting
- **Parallel Processing**: Non-blocking threading for responsive UI
- **Content Extraction**: Advanced HTML parsing with readability optimization

### 🧠 AI & Analysis
- **Credibility Scoring**: Domain reputation, content quality, spam detection
- **Sentiment Analysis**: Polarity and subjectivity measurement
- **Named Entity Recognition (NER)**: Extracts persons, organizations, locations, products
- **Keyphrases Extraction**: Identifies top topics and their frequency
- **Language Detection**: Automatic language identification
- **Readability Metrics**: Sentence complexity and readability scoring

### 📊 Insights & Reasoning
- **Consensus Detection**: Identifies common themes across sources
- **Credibility Aggregation**: Overall credibility score from multiple sources
- **Topic Clustering**: Groups related information automatically
- **Language Distribution**: Multilingual analysis support
- **Source Ranking**: Top credible sources highlighted

### 🎨 User Interfaces
- **GUI (DeepSearchGUI.py)**: Beautiful dark-themed interface with:
  - Real-time search progress
  - Insights panel with key metrics
  - Detailed analysis view
  - Click-to-expand result details
  - Export to JSON & CSV
  
- **CLI (DeepSearch.py)**: Command-line interface for:
  - Batch processing
  - Scripting integration
  - Server deployment

---

## 📋 Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Step 1: Clone/Download
```bash
cd "C:\Users\... "
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Download NLP Models
```bash
python -m spacy download en_core_web_sm
```

### Step 4: Verify Installation
```bash
python -c "import customtkinter, spacy, requests; print('✓ All dependencies installed')"
```

---

## 🚀 Usage

### GUI Mode (Recommended)
```bash
python DeepSearchGUI.py
```

**Features:**
- Enter search query in the search box
- Adjust search parameters (max results, fetch depth, delay)
- View real-time insights and analysis
- Click on results for detailed information
- Export results as JSON or CSV

### CLI Mode
```bash
# Basic search
python DeepSearch.py "your query"

# With options
python DeepSearch.py "your query" --max-results 20 --max-fetch 10 --delay 1.5

# Save results
python DeepSearch.py "your query" --save results.json
```

**Options:**
```
  --max-results    Maximum search hits to collect (default: 15)
  --max-fetch      Maximum pages to fetch and analyze (default: 5)
  --delay          Delay between fetches in seconds (default: 1.0)
  --save           Save JSON output to specified file
```

---

## 📊 Output Analysis

### Credibility Score (0-1)
- `0.90+` - Highly credible (academic, news, government)
- `0.70-0.90` - Credible with caveats
- `0.50-0.70` - Mixed credibility
- `<0.50` - Low credibility (spam indicators)

### Sentiment Analysis
- **Positive**: Optimistic/favorable language (polarity > 0.1)
- **Negative**: Critical/unfavorable language (polarity < -0.1)
- **Neutral**: Balanced/factual language

### Named Entities
- **PERSON**: Individual names
- **ORG**: Organizations and companies
- **GPE**: Geographical/political entities
- **PRODUCT**: Products and services

---

## 🔒 Ethics & Privacy

✅ **What DeepSearch Does:**
- Searches public web content only
- Respects `robots.txt` and site Terms of Service
- Implements polite rate limiting
- No authentication bypass
- No personal data scraping without consent

❌ **What DeepSearch Does NOT Do:**
- Access private/restricted resources
- Bypass authentication systems
- Collect personal data unethically
- Violate copyright protections
- Engage in unauthorized crawling

**Always ensure you have permission and comply with local laws before using this tool for data collection.**

---

## 📁 Project Structure

```
DeepSearch/
├── DeepSearch.py          # Core search & analysis engine
├── DeepSearchGUI.py       # Beautiful GUI interface
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── results/              # (auto-created) Saved results
    └── results.json      # Example export
    └── results.csv       # Example export
```

---

## 🔧 Configuration

### Adjustable Parameters

In `DeepSearchGUI.py` or CLI:

```python
# Search depth
max_results = 15   # 5-30 recommended
max_fetch = 5      # 1-10 recommended
delay = 1.0        # seconds between requests
```

### Domain Credibility Weights

Edit in `DeepSearch.py`:

```python
CREDIBLE_DOMAINS = {
    "wikipedia.org": 0.95,
    "edu": 0.90,
    "gov": 0.88,
    "bbc.com": 0.90,
    # Add more as needed
}
```

---

## 📈 Example Output

```
Query: artificial intelligence ethics
=================================================================================

🎯 INSIGHTS:
  Overall Credibility: 0.876
  Key Topics: ethics, ai, machine, learning, data, regulation
  Top Sources: 3

[1] ✓ The Ethics of Artificial Intelligence
    URL: https://example.com/ai-ethics
    Credibility: 0.92 | Words: 2847
    Sentiment: Neutral (polarity: 0.02)
    Key Phrases: artificial intelligence, machine learning, ethics, regulation
    Entities: ORG: OpenAI, DeepMind | PERSON: Elon Musk

[2] ✗ AI News Today
    URL: https://example.com/ai-news
    Credibility: 0.65 | Words: 156
```

---

## 🐛 Troubleshooting

### Issue: "ddgs not installed"
```bash
pip install ddgs
```

### Issue: "spacy model not found"
```bash
python -m spacy download en_core_web_sm
```

### Issue: "customtkinter import error"
```bash
pip install --upgrade customtkinter
```

### Issue: GUI won't open
```bash
# Check all dependencies
pip install -r requirements.txt --upgrade
```

### Issue: Slow search
- Reduce `max_fetch` parameter
- Increase `delay` to respect rate limits
- Use fewer `max_results`

---

## 🚀 Performance Tips

1. **Faster Searches**: Reduce `max_fetch` and `delay`
2. **Better Analysis**: Increase `max_fetch` and use smaller `delay`
3. **Batch Processing**: Use CLI for multiple queries
4. **Memory**: Works well on 4GB+ RAM machines
5. **Network**: Ensure stable internet connection

---

## 📚 API Reference

### `deep_search(query, max_results=10, max_fetch=5, delay=1.0)`

**Parameters:**
- `query` (str): Search query
- `max_results` (int): Number of search hits
- `max_fetch` (int): Pages to fetch and analyze
- `delay` (float): Seconds between requests

**Returns:** Dictionary with:
```python
{
    "query": "search term",
    "timestamp": "2025-11-28T18:59:56",
    "results": [...],
    "insights": {
        "overall_credibility": 0.876,
        "key_topics": {...},
        "top_sources": [...],
        "language_distribution": {...}
    }
}
```

---

## 🤝 Contributing

Found a bug? Have a feature request?

1. Test thoroughly
2. Document changes
3. Ensure ethical compliance
4. Submit with examples

---

## 📄 License

MIT License - Free for personal and commercial use

---

## ⚖️ Disclaimer

**DeepSearch is provided as-is for educational and research purposes.** Users are responsible for:
- Complying with local laws and regulations
- Respecting website Terms of Service
- Obtaining proper permissions
- Ethical use of collected data
- Protecting privacy of individuals

**The author accepts no liability for misuse.**

---

## 🌟 Future Features

- [ ] GraphQL support for structured queries
- [ ] Machine learning classification
- [ ] Automatic fact-checking
- [ ] Real-time collaboration
- [ ] Mobile app
- [ ] API server
- [ ] Database integration
- [ ] Advanced visualization dashboard

---

## 📞 Support

- 📧 Email: []
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions

---

## 🙏 Acknowledgments

Built with:
- [DuckDuckGo Search](https://www.duckduckgo.com)
- [spaCy](https://spacy.io)
- [TextBlob](https://textblob.readthedocs.io)
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup)

---

**Made with ❤️ for researchers, developers, and curious minds.**

*Last Updated: December 4, 2025*
