from pytrends.request import TrendReq
import feedparser
from googleapiclient.discovery import build
from datetime import datetime
import time
import os
import random

class TrendDataCollector:
    def __init__(self):
        # Google Trends
        self.pytrends = TrendReq(hl='el-GR', tz=360, timeout=(10,25))
        # YouTube Key
        self.youtube_key = os.getenv('YOUTUBE_API_KEY', '')

    def get_google_trends(self, region='GR', limit=20):
        print("Scanning Google Trends...")
        try:
            time.sleep(random.uniform(1, 3))
            trending = self.pytrends.trending_searches(pn=region.lower())
            results = []

            for keyword in trending[0][:5]:
                try:
                    self.pytrends.build_payload([keyword], timeframe='now 7-d')
                    interest = self.pytrends.interest_over_time()

                    if not interest.empty:
                        recent = interest[keyword].tail(1).values[0]
                        baseline = interest[keyword].head(1).values[0]
                        
                        if baseline > 0:
                            velocity = ((recent - baseline) / baseline) * 100
                        else:
                            velocity = 100 if recent > 0 else 0

                        results.append({
                            'keyword': keyword,
                            'source': 'google',
                            'volume': int(recent),
                            'velocity': round(velocity, 2),
                            'country': region
                        })
                    time.sleep(2)
                except Exception:
                    continue
            return results
        except Exception:
            return []

    def get_reddit_trends(self, subreddits=None, limit=10):
        print("Scanning Reddit (via RSS)...")
        if subreddits is None:
            subreddits = ['greece', 'buyitforlife', 'Entrepreneur', 'sidehustle']

        results = []
        try:
            for sub_name in subreddits:
                rss_url = f"https://www.reddit.com/r/{sub_name}/rising.rss"
                feed = feedparser.parse(rss_url)

                for entry in feed.entries[:limit]:
                    published_time = datetime(*entry.published_parsed[:6])
                    age_hours = (datetime.utcnow() - published_time).total_seconds() / 3600
                    velocity = 100 / age_hours if age_hours > 0.1 else 100
                    main_keyword = ' '.join(entry.title.lower().split()[:4])

                    results.append({
                        'keyword': main_keyword,
                        'source': f'reddit_{sub_name}',
                        'volume': 0,
                        'velocity': round(velocity, 2),
                        'country': 'GLOBAL'
                    })
                time.sleep(1)
        except Exception as e:
            print(f"Reddit RSS error: {e}")

        return results

    def get_youtube_trends(self, region='GR', limit=10):
        if not self.youtube_key:
            print("YouTube API Key missing.")
            return []

        print("Scanning YouTube...")
        results = []
        try:
            youtube = build('youtube', 'v3', developerKey=self.youtube_key)
            request = youtube.videos().list(
                part='snippet,statistics',
                chart='mostPopular',
                regionCode=region,
                maxResults=limit
            )
            response = request.execute()

            for item in response.get('items', []):
                title = item['snippet']['title']
                views = int(item['statistics'].get('viewCount', 0))
                main_keyword = ' '.join(title.lower().split()[:4])

                results.append({
                    'keyword': main_keyword,
                    'source': 'youtube',
                    'volume': views,
                    'velocity': 0,
                    'country': region
                })
        except Exception as e:
            print(f"YouTube error: {e}")

        return results