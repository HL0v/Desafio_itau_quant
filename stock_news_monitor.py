
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
import apikeys

# Configure logging
logging.basicConfig(
    filename='soy.log',
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
soy_logger = logging.getLogger('soy')

@dataclass
class NewsArticle:
    """Data structure for a news article."""
    title: str
    url: str
    published_at: str
    description: str
    matched_keywords: List[str] = field(default_factory=list)
    ticker: Optional[str] = None

@dataclass
class MonitorConfig:
    api_key: str = apikeys.news_api_key
    refresh_interval: int = 30
    price_moving_keywords: List[str] = field(default_factory=lambda: [

      #  """coringas"""
       'commodities', 

        'plantio', 'colheita',

     #   """fatores naturais"""
        'clima', 'chuva',
        'seca', 'pragas',
        'doenças', 'elninho',
        'geada', 'temperatura',
        'granizo', 'inundações',
     
        
       # """fatores de estrito mercado"""
        'oferta', 'demanda',

        'safra', 'exportação', 'importação',

        'especulação','tick de soja', 
        'cotação da soja','contrato futuro soja',
        

        #"""fatores geopolíticos"""
        'Guerra', 'sanções',
        'China', 'guerra comercial', 
        'política agrícola', 'subsídios', 
        'tarifas', 'acordo comercial',
        

    ])

class NewsMonitor:  
    def _build_ticker_mapping(self) -> Dict[str, str]:
        """Build a mapping of tickers to company names for better search results."""
        # Basic mapping - could be extended with a comprehensive database
        return {
            
            'Brasil' : 'comercio de soja'
        }
        # Return mapping for requested tickers
        
    def __init__(self, config: MonitorConfig):
        self.config = config
        self.newsapi = NewsApiClient(api_key=config.api_key)
        self.processed_articles: Set[str] = set()
        self.ticker_to_company = self._build_ticker_mapping()
        # Set tickers from the mapping
        self.config.tickers = list(self.ticker_to_company.keys())
    

    

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
            soy_logger.debug(f"Searching for ticker {ticker} with query: {query}")

            # Search for articles from the last 14 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=14)
            

            articles = self.newsapi.get_everything(
                q=query,
                language='pt',
                sort_by='publishedAt',
                from_param=start_date.strftime("%Y-%m-%d"),
                to=end_date.strftime('%Y-%m-%d'),
                page_size=20
            )
            
              # Add debug logging for API response
            soy_logger.info(f"Found {len(articles.get('articles', []))} total articles for {ticker}")

            news_articles = []
            
            for article in articles.get('articles', []):
                # Skip if already processed
                if article['url'] in self.processed_articles:
                    continue
                
                news_article = NewsArticle(
                    title=article.get('title', 'No title'),
                    url=article['url'],
                    published_at=article.get('publishedAt', ''),
                    description=article.get('description', ''),
                    matched_keywords=[],  # We'll fill this later
                    ticker=ticker
                )

                # Extract matched keywords from title and description
                article_text = f"{article.get('title', '')} {article.get('description', '')}"
                matched_keywords = self._extract_matched_keywords(article_text)

                # Debug log for keyword matching
                soy_logger.info(f"Article: {news_article.title}")
                soy_logger.info(f"Matched keywords: {matched_keywords}")
                
                # Only include articles with matched keywords
                news_article.matched_keywords = matched_keywords
                if matched_keywords:
                    news_articles.append(news_article)
                    self.processed_articles.add(article['url'])
            
            return news_articles
            
        except Exception as e:
            soy_logger.error(f"Error fetching news for {ticker}: {e}")
            return []
    
    def analyze_with_ai(self, url: str) -> Dict:
        """
        Placeholder function for AI analysis of the article.
        This should be implemented with your preferred AI service.
        """
        # TODO: Implement actual AI analysis
        # This could integrate with OpenAI, Claude, or other AI services
        soy_logger.info(f"🤖 AI Analysis requested for: {url}")
        
        return {
            "sentiment": "neutral",
            "impact_score": 0.5,
            "summary": "AI analysis not yet implemented",
            "recommendation": "monitor"
        }
    
    def process_article(self, article: NewsArticle) -> None:
        """Process a single article - print details and trigger AI analysis."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        soy_logger.info(f"📈 soy news alert - {timestamp}")
        soy_logger.info(f"\n{'='*80}")
        soy_logger.info(f"{'='*80}")
        soy_logger.info(f"Ticker: {article.ticker}")
        soy_logger.info(f"Title: {article.title}")
        soy_logger.info(f"Published: {article.published_at}")
        soy_logger.info(f"URL: {article.url}")
        soy_logger.info(f"Matched Keywords: {', '.join(article.matched_keywords)}")

        if article.description:
            desc = str(article.description)
            truncated_desc = desc[:200] + "..." if len(desc) > 200 else desc
            soy_logger.info(f"Description: {truncated_desc}\n")
        
        # Trigger AI analysis
        try:
            ai_result = self.analyze_with_ai(article.url)
            soy_logger.info(f"AI Analysis: {ai_result.get('summary', 'No summary available')}\n")
        except Exception as e:
            soy_logger.error(f"Error in AI analysis: {e}")
            soy_logger.info(f"{'='*80}\n")


    def check_news(self) -> None:
        """Check news for all configured tickers."""
        soy_logger.info(f"🔍 Checking news for tickers: {', '.join(self.config.tickers)}")
        
        total_articles = 0
        
        for ticker in self.config.tickers:
            articles = self.fetch_news_for_ticker(ticker)
            
            for article in articles:
                self.process_article(article)
                total_articles += 1
        
        if total_articles == 0:
            soy_logger.info("No new relevant articles found")
        else:
            soy_logger.info(f"Found {total_articles} new relevant articles")
    
    def start_monitoring(self) -> None:
        """Start the continuous monitoring process."""
        soy_logger.info(f"\n\n🚀 Starting Soy News Monitor\n")
        soy_logger.info(f"Monitoring tickers: {', '.join(self.config.tickers)}\n")
        soy_logger.info(f"Refresh interval: {self.config.refresh_interval} seconds\n")
        soy_logger.info(f"Keywords: {', '.join(self.config.price_moving_keywords[:5])}... (+{len(self.config.price_moving_keywords)-5} more)\n")
        soy_logger.info("Press Ctrl+C to stop\n")
        soy_logger.info(f"{'='*80}\n")
        
        
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
            soy_logger.info("\n👋 Stopping Stock News Monitor...")
            soy_logger.info("Monitor stopped by user")

def main():
    """Main entry point."""
    reqs = argparse.ArgumentParser(description='Monitor stock news for \
                                   price-moving events')
    reqs.add_argument(
        '--interval',
        type=int,
        default=30,
        help='Refresh interval in seconds (default: 30)'
    )

    init_reqs = reqs.parse_args()
    
    # Create configuration
    config =  MonitorConfig(
        api_key= apikeys.news_api_key,
        refresh_interval=init_reqs.interval
    )
    # Create and start monitor
    monitor = NewsMonitor(config)
    monitor.start_monitoring()

if __name__ == "__main__":
    main()