"""Source trust lookup shared by ingestion and retrieval without package cycles."""
from urllib.parse import urlparse

from apps.articles.models import SourceRegistry

DEFAULT_SOURCES = {
    "NASA": ("nasa.gov", "official", 1, 1),
    "Reuters": ("reuters.com", "reputable_news", 2, 2),
    "Associated Press": ("apnews.com", "reputable_news", 2, 2),
    "BBC": ("bbc.com", "reputable_news", 2, 2),
    "Wikipedia": ("wikipedia.org", "reference", 3, 3),
    "Google News": ("news.google.com", "general_news", 4, 4),
    "The Times of India": ("indiatimes.com", "reputable_news", 2, 2),
    "The Guardian": ("theguardian.com", "reputable_news", 2, 2),
    "CNN": ("cnn.com", "reputable_news", 2, 2),
    "The New York Times": ("nytimes.com", "reputable_news", 2, 2),
    "Washington Post": ("washingtonpost.com", "reputable_news", 2, 2),
    "Financial Times": ("ft.com", "reputable_news", 2, 2),
    "The Wall Street Journal": ("wsj.com", "reputable_news", 2, 2),
    "The Telegraph": ("telegraph.co.uk", "reputable_news", 2, 2),
    "The Independent": ("independent.co.uk", "reputable_news", 2, 2),
    "Sky News": ("skynews.com", "reputable_news", 2, 2),
    "NBC News": ("nbcnews.com", "reputable_news", 2, 2),
    "ABC News": ("abcnews.go.com", "reputable_news", 2, 2),
    "CNBC": ("cnbc.com", "reputable_news", 2, 2),
    "MarketWatch": ("marketwatch.com", "reputable_news", 2, 2),
    "TechCrunch": ("techcrunch.com", "general_news", 4, 4),
    "The Hindu": ("thehindu.com", "general_news", 4, 4),
    "The Economic Times": ("economictimes.indiatimes.com", "general_news", 4, 4),
    "The Indian Express": ("indianexpress.com", "general_news", 4, 4),
    "Live Law": ("livelaw.in", "general_news", 4, 4),
    "Notebookcheck": ("notebookcheck.net", "general_news", 4, 4),
    "Barca Universal": ("barcauniversal.com", "general_news", 4, 4),
    "Chron": ("chron.com", "general_news", 4, 4),
    "Crude Oil Prices Today | OilPrice.com": ("oilprice.com", "general_news", 4, 4),
    "Football365": ("football365.com", "general_news", 4, 4),
    "Gizmochina": ("gizmochina.com", "general_news", 4, 4),
    "Managing Madrid": ("managingmadrid.com", "general_news", 4, 4),
    "Techgenyz": ("techgenyz.com", "general_news", 4, 4),
    "The Brighter Side of News": ("thebrighterside.news", "general_news", 4, 4),
    "The News Minute": ("thenewsminute.com", "general_news", 4, 4),
    "TradingView": ("tradingview.com", "general_news", 4, 4),
    "indiantelevision.com": ("indiantelevision.com", "general_news", 4, 4),
    "livemint.com": ("livemint.com", "general_news", 4, 4),
}
TYPE_SCORES = {"official": 1.0, "reputable_news": .90, "reference": .78, "general_news": .65, "web": .35}


def source_metadata(source: str, url: str = "") -> dict:
    domain = urlparse(url).netloc.lower().removeprefix("www.")
    try:
        entry = SourceRegistry.objects.filter(active=True).filter(source__iexact=source).first()
        if not entry and domain:
            entry = SourceRegistry.objects.filter(active=True, domain__iexact=domain).first()
    except Exception:
        entry = None
    if entry:
        return {"source_type": entry.source_type, "trust_tier": entry.trust_tier, "priority": entry.priority, "trust_score": TYPE_SCORES[entry.source_type]}
    for name, (known_domain, source_type, tier, priority) in DEFAULT_SOURCES.items():
        if source.lower() == name.lower() or domain.endswith(known_domain):
            return {"source_type": source_type, "trust_tier": tier, "priority": priority, "trust_score": TYPE_SCORES[source_type]}
    return {"source_type": "web", "trust_tier": 5, "priority": 5, "trust_score": TYPE_SCORES["web"]}
