import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from dataclasses import dataclass
from typing import List
import time
import io
import pypdf

@dataclass
class PageData:
    url: str
    title: str
    text: str
    links: List[str]
    pdfs: List[str]
    images: List[str]

class WebScraper:
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0"}

    def fetch(self, url: str):
        response = requests.get(url, headers=self.headers, timeout=10)
        response.raise_for_status()
        response.encoding = "utf-8"
        content_type = response.headers.get("Content-Type", "")
        return response, content_type

    def scrape(self, url: str) -> PageData:
        response, content_type = self.fetch(url)
        if "application/pdf" in content_type:
            return self.parse_pdf(response.content, url)
        elif "text/html" in content_type:
            return self.parse_html(response.text, url)
        else:
            print(f"⚠️ Unsupported content: {content_type}")
            return None

    def parse_html(self, html: str, base_url: str) -> PageData:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        title = soup.title.text if soup.title else ""
        main = soup.find("main") or soup.find("article") or soup.body
        text = main.get_text(separator=" ", strip=True) if main else ""

        links, pdfs, images = [], [], []
        for a in soup.find_all("a", href=True):
            full_url = urljoin(base_url, a["href"])
            if full_url.endswith(".pdf"):
                pdfs.append(full_url)
            else:
                links.append(full_url)

        for img in soup.find_all("img"):
            src = img.get("src")
            if src:
                images.append(urljoin(base_url, src))

        return PageData(
            url=base_url, title=title, text=text,
            links=list(set(links)), pdfs=list(set(pdfs)), images=list(set(images)),
        )

    def parse_pdf(self, pdf_bytes, url: str) -> PageData:
        try:
            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            text = ""
        
        return PageData(
            url=url, title="PDF Document", text=text,
            links=[], pdfs=[url], images=[]
        )

def crawl_website(start_url: str, max_pages: int = 5) -> List[PageData]:
    scraper = WebScraper()
    visited = set()
    queue = [start_url]
    results = []

    while queue and len(visited) < max_pages:
        url = queue.pop(0)
        if url in visited: continue
        try:
            print(f"🔍 Scraping: {url}")
            page_data = scraper.scrape(url)
            if not page_data: continue
            visited.add(url)
            results.append(page_data)
            for link in page_data.links:
                if link not in visited:
                    queue.append(link)
            time.sleep(1)
        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")

    return results