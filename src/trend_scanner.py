import os
import asyncio
from datetime import datetime
from supabase import create_client, Client
from data_sources import TrendDataCollector
from scoring import MonetizationScorer
from notifications import TelegramNotifier

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
HIGH_SCORE_THRESHOLD = 8.5

class TrendProphet:
    def __init__(self):
        if SUPABASE_URL and SUPABASE_KEY:
            self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        else:
            self.supabase = None
            
        self.collector = TrendDataCollector()
        self.scorer = MonetizationScorer()
        self.notifier = TelegramNotifier()

    def collect_trends(self):
        all_trends = []
        all_trends.extend(self.collector.get_google_trends(region='GR', limit=20))
        all_trends.extend(self.collector.get_reddit_trends(limit=5))
        all_trends.extend(self.collector.get_youtube_trends(region='GR', limit=10))
        print(f"Collected {len(all_trends)} trends")
        return all_trends

    def score_and_filter(self, trends):
        scored_trends = []
        for trend in trends:
            score = self.scorer.score(trend)
            trend['monetization_score'] = score
            trend['detected_at'] = datetime.utcnow().isoformat()

            if score >= HIGH_SCORE_THRESHOLD:
                trend['strategy'] = self.scorer.get_recommended_strategy(trend, score)
                scored_trends.append(trend)
        return scored_trends

    def save_to_database(self, trends):
        if not trends or not self.supabase: return
        try:
            for trend in trends:
                self.supabase.table('trends').insert({
                    'keyword': trend['keyword'],
                    'source': trend['source'],
                    'volume': trend.get('volume', 0),
                    'velocity': trend.get('velocity', 0),
                    'monetization_score': trend['monetization_score'],
                    'country': trend.get('country', 'GR')
                }).execute()
            print(f"Saved {len(trends)} trends to database")
        except Exception as e:
            print(f"Database error: {e}")

    async def run(self):
        print(f"Trend Prophet - {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        trends = self.collect_trends()
        high_score_trends = self.score_and_filter(trends)

        if trends: self.save_to_database(trends)
        if high_score_trends:
            await self.notifier.send_alert(high_score_trends)
        else:
            print("No high-score trends this round")

if __name__ == "__main__":
    prophet = TrendProphet()
    asyncio.run(prophet.run())