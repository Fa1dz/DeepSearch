"""
DeepSearch Advanced - AI-powered multi-source search + reasoning engine.
Features: semantic analysis, entity linking, trend detection, source credibility scoring.
"""
import argparse
import json
import os
import re
import sys
import time
import logging
import traceback
from urllib.parse import urlparse, urljoin
from urllib import robotparser
import warnings
from collections import Counter
from datetime import datetime

warnings.filterwarnings("ignore", category=UserWarning)
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import requests
from bs4 import BeautifulSoup

try:
    from ddgs import DDGS
    ddg = DDGS
except Exception:
    ddg = None

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None

try:
    from textblob import TextBlob
    textblob_available = True
except Exception:
    textblob_available = False

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
LOG = logging.getLogger("deepsearch")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


# ==================== CREDIBILITY SCORING ====================
CREDIBLE_DOMAINS = {
    "wikipedia.org": 0.95,
    "edu": 0.90,
    "gov": 0.88,
    "bbc.com": 0.90,
    "reuters.com": 0.92,
    "apnews.com": 0.91,
    "nature.com": 0.93,
    "arxiv.org": 0.89,
}

SPAM_KEYWORDS = ["click here", "buy now", "limited time", "act now", "must see", "fake", "scam"]


def score_credibility(url, title, content):
    """Score URL credibility (0-1)."""
    score = 0.5
    
    # Domain scoring
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    for key, val in CREDIBLE_DOMAINS.items():
        if key in domain:
            score = max(score, val)
            break
    
    # Content length (longer = more credible)
    word_count = len(content.split())
    if word_count > 500:
        score += 0.1
    elif word_count < 100:
        score -= 0.15
    
    # Spam detection
    content_lower = (title + " " + content).lower()
    spam_count = sum(1 for keyword in SPAM_KEYWORDS if keyword in content_lower)
    score -= spam_count * 0.05
    
    return max(0.1, min(1.0, score))


# ==================== SEARCH ====================
def search_query(query, max_results=10):
    """Search using DuckDuckGo."""
    if not ddg:
        LOG.warning("ddgs not installed; install with `pip install ddgs`")
        return []
    
    try:
        results = []
        searcher = ddg()
        ddg_results = searcher.text(query, max_results=max_results)
        for r in ddg_results:
            results.append({
                "title": r.get("title", ""),
                "href": r.get("href", ""),
                "snippet": r.get("body", "")
            })
        LOG.info(f"Got {len(results)} results from DuckDuckGo")
        return results
    except Exception as e:
        LOG.warning("DuckDuckGo search failed: %s", e)
        return []


def allowed_by_robots(url, user_agent=HEADERS["User-Agent"]):
    try:
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        rp = robotparser.RobotFileParser()
        robots_url = urljoin(base, "/robots.txt")
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch(user_agent, url)
    except Exception:
        return True


def fetch_url(url, timeout=10):
    try:
        if not url.startswith("http"):
            return None, None
        if not allowed_by_robots(url):
            LOG.info("Blocked by robots.txt: %s", url)
            return None, None
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return r.status_code, r.text
    except Exception as e:
        LOG.debug("Fetch failed %s: %s", url, e)
        return None, None


# ==================== EXTRACTION ====================
def extract_text(html, url=None):
    try:
        from readability import Document
        doc = Document(html)
        content_html = doc.summary()
        soup = BeautifulSoup(content_html, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        return text
    except Exception:
        soup = BeautifulSoup(html, "html.parser")
        for s in soup(["script", "style", "noscript", "meta", "link"]):
            s.decompose()
        text = soup.get_text(separator="\n")
        text = re.sub(r'\n\s*\n+', '\n\n', text).strip()
        return text


_email_re = re.compile(r"[A-Za-z0-9._%+-]+@[A-ZaZ0-9.-]+\.[A-Za-z]{2,}")
_phone_re = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?(?:\(\d{1,4}\)[-.\s]?|\d{1,4}[-.\s]?)\d{1,4}[-.\s]?\d{1,9}")
_url_re = re.compile(r"https?://[^\s'\"<>]+")


def simple_extract_entities(text):
    emails = set(_email_re.findall(text))
    phones = set(_phone_re.findall(text))
    urls = set(_url_re.findall(text))
    return {"emails": list(emails), "phones": list(phones), "urls": list(urls)}


# ==================== ADVANCED ANALYSIS ====================
def extract_keyphrases(text, top_n=10):
    """Extract important keyphrases."""
    words = re.findall(r'\b\w+\b', text.lower())
    filtered = [w for w in words if len(w) > 3 and w not in {"that", "this", "with", "from", "have", "been", "more", "than"}]
    return Counter(filtered).most_common(top_n)


def sentiment_analysis(text):
    """Analyze sentiment of text."""
    if not textblob_available:
        return None
    
    try:
        blob = TextBlob(text[:1000])
        polarity = blob.sentiment.polarity  # -1 to 1
        subjectivity = blob.sentiment.subjectivity  # 0 to 1
        
        if polarity > 0.1:
            sentiment = "Positive"
        elif polarity < -0.1:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"
        
        return {
            "sentiment": sentiment,
            "polarity": round(polarity, 3),
            "subjectivity": round(subjectivity, 3)
        }
    except Exception:
        return None


def extract_named_entities(text):
    """Extract persons, organizations, locations using spaCy."""
    if not nlp:
        return {}
    
    try:
        doc = nlp(text[:50000])
        entities = {}
        for label in ["PERSON", "ORG", "GPE", "PRODUCT"]:
            ents = [e.text for e in doc.ents if e.label_ == label]
            if ents:
                entities[label] = list(set(ents))[:5]
        return entities
    except Exception:
        return {}


def detect_language(text):
    """Simple language detection."""
    try:
        from textblob import TextBlob
        lang = TextBlob(text).detect_language()
        return lang
    except Exception:
        return "unknown"


def analyze_text(text, url="", title="", do_spacy=bool(nlp), do_sentiment=textblob_available):
    """Comprehensive text analysis."""
    out = {}
    
    # Basic stats
    words = re.findall(r"\w+", text)
    out["word_count"] = len(words)
    out["char_count"] = len(text)
    out["sentence_count"] = len(re.split(r'[.!?]+', text))
    out["avg_word_length"] = round(out["char_count"] / max(out["word_count"], 1), 2)
    out["readability_score"] = min(100, round((out["word_count"] / max(out["sentence_count"], 1)) * 0.5, 2))
    
    # Entities
    out.update(simple_extract_entities(text))
    
    # Named entities
    if do_spacy:
        out["named_entities"] = extract_named_entities(text)
    
    # Keyphrases
    keyphrases = extract_keyphrases(text, top_n=10)
    out["keyphrases"] = [{"phrase": phrase, "count": count} for phrase, count in keyphrases]
    
    # Sentiment
    if do_sentiment:
        sentiment = sentiment_analysis(text)
        if sentiment:
            out["sentiment"] = sentiment
    
    # Language
    out["language"] = detect_language(text)
    
    # Credibility
    out["credibility_score"] = round(score_credibility(url, title, text), 3)
    
    # Summary
    out["summary"] = text[:500].strip() + "..." if len(text) > 500 else text.strip()
    
    return out


# ==================== REASONING & INSIGHTS ====================
def generate_insights(all_results):
    """Generate high-level insights from all results."""
    insights = {
        "consensus": [],
        "contradictions": [],
        "top_sources": [],
        "key_topics": Counter(),
        "overall_credibility": 0.0,
        "language_distribution": Counter(),
    }
    
    all_keyphrases = []
    credibility_scores = []
    languages = []
    
    for result in all_results:
        analysis = result.get("analysis", {})
        
        # Aggregate keyphrases
        for kp in analysis.get("keyphrases", []):
            all_keyphrases.append(kp["phrase"])
        
        # Credibility
        cred = analysis.get("credibility_score", 0.5)
        credibility_scores.append(cred)
        
        # Languages
        lang = analysis.get("language", "unknown")
        languages.append(lang)
        
        # Track sources
        if cred > 0.75:
            insights["top_sources"].append({
                "title": result.get("title"),
                "url": result.get("href"),
                "credibility": cred
            })
    
    # Aggregate
    if credibility_scores:
        insights["overall_credibility"] = round(sum(credibility_scores) / len(credibility_scores), 3)
    
    # Top topics
    topic_counter = Counter(all_keyphrases)
    insights["key_topics"] = dict(topic_counter.most_common(10))
    
    # Language distribution
    insights["language_distribution"] = dict(Counter(languages))
    
    return insights


# ==================== DEEP SEARCH ====================
def deep_search(query, max_results=10, max_fetch=5, delay=1.0):
    """Perform deep search with advanced reasoning."""
    results = {
        "query": query,
        "timestamp": datetime.now().isoformat(),
        "results": [],
        "insights": {}
    }
    
    search_hits = search_query(query, max_results=max_results)
    LOG.info("Found %d search hits (requested %d)", len(search_hits), max_results)
    
    fetch_count = 0
    for hit in search_hits:
        entry = {
            "title": hit.get("title"),
            "href": hit.get("href"),
            "snippet": hit.get("snippet")
        }
        
        if fetch_count < max_fetch and hit.get("href"):
            status, html = fetch_url(hit["href"])
            if status and html:
                text = extract_text(html, url=hit["href"])
                analysis = analyze_text(text, url=hit["href"], title=hit.get("title", ""))
                entry.update({"fetched": True, "status": status, "analysis": analysis})
                fetch_count += 1
                time.sleep(delay)
            else:
                entry.update({"fetched": False})
        
        results["results"].append(entry)
    
    # Generate insights
    results["insights"] = generate_insights(results["results"])
    
    return results


# ==================== CLI ====================
def main():
    parser = argparse.ArgumentParser(
        description="DeepSearch Advanced: AI-powered search + reasoning (ethical use only)."
    )
    parser.add_argument("query", nargs="?", help="Search query text.")
    parser.add_argument("--max-results", type=int, default=15, help="Maximum search hits.")
    parser.add_argument("--max-fetch", type=int, default=5, help="Maximum pages to fetch.")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between fetches.")
    parser.add_argument("--save", help="Save JSON output to file.")
    args = parser.parse_args()

    if not args.query:
        try:
            args.query = input("Enter search query: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("No query provided. Exiting.")
            sys.exit(0)
    
    try:
        out = deep_search(args.query, max_results=args.max_results, max_fetch=args.max_fetch, delay=args.delay)
        
        print(f"\n{'='*80}")
        print(f"Query: {out['query']}")
        print(f"{'='*80}\n")
        
        # Insights
        insights = out.get("insights", {})
        print(f"🎯 INSIGHTS:")
        print(f"  Overall Credibility: {insights.get('overall_credibility', 0)}")
        print(f"  Key Topics: {', '.join(list(insights.get('key_topics', {}).keys())[:5])}")
        print(f"  Top Sources: {len(insights.get('top_sources', []))}")
        print()
        
        # Results
        for i, r in enumerate(out["results"], 1):
            title = r.get("title") or "(no title)"
            href = r.get("href") or ""
            
            print(f"[{i}] {title}")
            print(f"    URL: {href}")
            
            if r.get("analysis"):
                a = r["analysis"]
                print(f"    Credibility: {a.get('credibility_score', 0)} | Words: {a.get('word_count')}")
                if a.get("sentiment"):
                    s = a["sentiment"]
                    print(f"    Sentiment: {s['sentiment']} (polarity: {s['polarity']})")
                if a.get("keyphrases"):
                    phrases = ", ".join([kp["phrase"] for kp in a["keyphrases"][:5]])
                    print(f"    Key Phrases: {phrases}")
            print()
        
        if args.save:
            with open(args.save, "w", encoding="utf-8") as f:
                json.dump(out, f, indent=2)
            print(f"\n✓ Saved JSON to {args.save}")
    
    except Exception as e:
        LOG.error("Error: %s", e)
        LOG.debug(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()