
"""
Stock News Monitor
Monitors news for specified companies and identifies articles that could impact stock prices.
"""

import argparse
import time
import schedule
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Set, Dict, Optional
from newsapi import NewsApiClient
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class NewsArticle:
    """Data structure for a news article."""
    title: str
    url: str
    published_at: str
    matched_keywords: List[str] = field(default_factory=list)
    ticker: Optional[str] = None

@dataclass
class MonitorConfig:
    """Configuration for the news monitor."""
    tickers: List[str]
    api_key: str 
    refresh_interval: int = 60
    price_moving_keywords: List[str] = field(default_factory=lambda: [
        """coringas"""
        'commodities', 'biodiesel',
        'biocombustíveis', 'estoques',
        'produção', 'consumo',
        'preço', 'preços',


        """fatores naturais"""
        'clima', 'chuva',
        'seca', 'pragas',
        'doenças',
        
        """fatores de estrito mercado"""
        'oferta', 'demanda',
        'dólar', 'câmbio',
        'safra', 'exportação', 'importação',
        'fundos de investimento', 'bolsa de Chicago',
        'especulação','tick de soja', 
        'cotação da soja',

        """fatores geopolíticos"""
        'Guerra', 'sanções',
        'China', 'guerra comercial', 
        'política agrícola', 'subsídios', 

 
    ])

class NewsMonitor:
    """Main class for monitoring stock-related news."""
    
    def __init__(self, config: MonitorConfig):
        self.config = config
        self.newsapi = NewsApiClient(api_key=config.api_key)
        self.processed_articles: Set[str] = set()  # Track processed URLs
        self.ticker_to_company: Dict[str, str] = self._build_ticker_mapping()
        
    def _build_ticker_mapping(self) -> Dict[str, str]:
        """Build a mapping of tickers to company names for better search results."""
        # Basic mapping - could be extended with a comprehensive database
        common_mappings = {
            'FUT SJC': 'Futuro de soja na B3',
            #'tick de soja':
            #'preço da soja':'preço da soja', 
            #'cotação da soja':
            #'mercado futuro':'mercado futuro', 
            #'sojaboi':'sojaboi', 
            'CME':'CME Group', 
            'NYSE':'NYSE indice composto', 
            'B3':'Bolsa B3', 
            'ADM':'Archer Daniels Midland', 
            'CARG':'Cargill', 
            'Bunge':'Bunge', 
            'Louis Dreyfus':'Louis Dreyfus', 
            'Amaggi':'Amaggi', 
            'SLC Agrícola':'SLC Agrícola', 
            'BrasilAgro':'BrasilAgro', 
            'Viterra':'Viterra', 
            'COFCO International':'COFCO International', 
            'Syngenta':'Syngenta', 
            'Bayer':'Bayer', 
            'BASF':'BASF', 
            'Mosaic':'Mosaic', 
            'Nutrien':'Nutrien',
            'ILPF':'relacao de preco soja e boi'
        }
        
        # Return mapping for requested tickers
        return {ticker: common_mappings.get(ticker, ticker) 
                for ticker in self.config.tickers}
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers={
            logging.FileHandler('stock_monitor.log'),
            logging.StreamHandler()  # keep console output
        }
    )

    logger = logging.getLogger(__name__)

    def _build_search_query(self, ticker: str) -> str:
        """Build search query for a specific ticker."""
        company_name = self.ticker_to_company.get(ticker, ticker)
        
        # Create query with ticker and company name
        base_query = f'"{ticker}" OR "{company_name}"'
        
        # Add keyword filters
        keyword_query = ' OR '.join([f'"{keyword}"' for keyword in self.config.price_moving_keywords])
        
        return f'({base_query}) AND ({keyword_query})'
    
    def _extract_matched_keywords(self, article_text: str) -> List[str]:
        """Extract which keywords matched in the article."""
        matched = []
        text_lower = article_text.lower()
        
        for keyword in self.config.price_moving_keywords:
            if keyword.lower() in text_lower:
                matched.append(keyword)
        
        return matched
    
    def fetch_news_for_ticker(self, ticker: str) -> List[NewsArticle]:
        """Fetch news articles for a specific ticker."""
        try:
            query = self._build_search_query(ticker)
            logger.debug(f"Searching for ticker {ticker} with query: {query}")

            # Search for articles from the last 7 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            

            articles = self.newsapi.get_everything(
                q=query,
                language='en',
                sort_by='publishedAt',
                from_param=start_date.strftime("%Y-%m-%d"),
                to=end_date.strftime('%Y-%m-%d'),
                page_size=20
            )
            
              # Add debug logging for API response
            logger.info(f"Found {len(articles.get('articles', []))} total articles for {ticker}")

            news_articles = []
            
            for article in articles.get('articles', []):
                # Skip if already processed
                if article['url'] in self.processed_articles:
                    continue
                
                news_article = NewsArticle(
                    title=article.get('title', 'No title'),
                    url=article['url'],
                    published_at=article.get('publishedAt', ''),
                    source=article.get('source', {}).get('name', 'Unknown'),
                    description=article.get('description', ''),
                    matched_keywords=[],  # We'll fill this later
                    ticker=ticker
                )

                # Extract matched keywords from title and description
                article_text = f"{article.get('title', '')} {article.get('description', '')}"
                matched_keywords = self._extract_matched_keywords(article_text)

                # Debug log for keyword matching
                logger.info(f"Article: {news_article.title}")
                logger.info(f"Matched keywords: {matched_keywords}")
                
                # Only include articles with matched keywords
                news_article.matched_keywords = matched_keywords
                if matched_keywords:
                    news_articles.append(news_article)
                    self.processed_articles.add(article['url'])
            
            return news_articles
            
        except Exception as e:
            logger.error(f"Error fetching news for {ticker}: {e}")
            return []
    
    def analyze_with_ai(self, url: str) -> Dict:
        """
        Placeholder function for AI analysis of the article.
        This should be implemented with your preferred AI service.
        """
        # TODO: Implement actual AI analysis
        # This could integrate with OpenAI, Claude, or other AI services
        logger.info(f"🤖 AI Analysis requested for: {url}")
        
        return {
            "sentiment": "neutral",
            "impact_score": 0.5,
            "summary": "AI analysis not yet implemented",
            "recommendation": "monitor"
        }
    
    def process_article(self, article: NewsArticle) -> None:
        """Process a single article - print details and trigger AI analysis."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with open("articles.log", "a", encoding="utf-8") as file:
            file.write(f"📈 STOCK NEWS ALERT - {timestamp}")
            file.write(f"\n{'='*80}")
            file.write(f"{'='*80}")
            file.write(f"Ticker: {article.ticker}")
            file.write(f"Title: {article.title}")
            file.write(f"Source: {article.source}")
            file.write(f"Published: {article.published_at}")
            file.write(f"URL: {article.url}")
            file.write(f"Matched Keywords: {', '.join(article.matched_keywords)}")

        if article.description:
            desc = str(article.description)
            truncated_desc = desc[:200] + "..." if len(desc) > 200 else desc
            with open("articles.log", "a", encoding="utf-8") as file:
                file.write(f"Description: {truncated_desc}\n")
        
        # Trigger AI analysis
        try:
            ai_result = self.analyze_with_ai(article.url)
            with open("articles.log", "a", encoding="utf-8") as file:
                file.write(f"AI Analysis: {ai_result.get('summary', 'No summary available')}\n")
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            with open("articles.log", "a", encoding="utf-8") as file:
                file.write(f"{'='*80}\n")
        
    
    def check_news(self) -> None:
        """Check news for all configured tickers."""
        logger.info(f"🔍 Checking news for tickers: {', '.join(self.config.tickers)}")
        
        total_articles = 0
        
        for ticker in self.config.tickers:
            articles = self.fetch_news_for_ticker(ticker)
            
            for article in articles:
                self.process_article(article)
                total_articles += 1
        
        if total_articles == 0:
            logger.info("No new relevant articles found")
        else:
            logger.info(f"Found {total_articles} new relevant articles")
    
    def start_monitoring(self) -> None:
        """Start the continuous monitoring process."""
        with open("articles.log", "a", encoding="utf-8") as file:
            file.write(f"\n\n🚀 Starting Stock News Monitor\n")
            file.write(f"Monitoring tickers: {', '.join(self.config.tickers)}\n")
            file.write(f"Refresh interval: {self.config.refresh_interval} seconds\n")
            file.write(f"Keywords: {', '.join(self.config.price_moving_keywords[:5])}... (+{len(self.config.price_moving_keywords)-5} more)\n")
            file.write("Press Ctrl+C to stop\n")
            file.write(f"{'='*80}\n")
        
        
        # Schedule the job
        schedule.every(self.config.refresh_interval).seconds.do(self.check_news)
        
        # Run initial check
        self.check_news()
        
        # Keep running
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            with open("articles.log", "a", encoding="utf-8") as file:
                file.write("\n👋 Stopping Stock News Monitor...")
            logger.info("Monitor stopped by user")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Monitor stock news for price-moving events')
    parser.add_argument(
        'tickers',
        nargs='+',
        help='monitor news for Apple, Google, and Microsoft stocks, ' \
        'checking every 5 minutes (300 seconds)'
    )
    parser.add_argument(
        '--api-key',
        required=True,
        help='c99a829bc5664f3abfd5905d54caf02e'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Refresh interval in seconds (default: 60)'
    )
    
    args = parser.parse_args()
    
    # Convert tickers to uppercase
    tickers = [ticker.upper() for ticker in args.tickers]
    
    # Create configuration
    config = MonitorConfig(
        tickers=tickers,
        api_key=args.api_key,
        refresh_interval=args.interval
    )
    
    # Create and start monitor
    monitor = NewsMonitor(config)
    monitor.start_monitoring()

if __name__ == "__main__":
    main()