class MonetizationScorer:

    COMMERCIAL_KEYWORDS = [
        'αγορά', 'buy', 'best', 'top', 'review', 'φθηνό', 'cheap',
        'προσφορά', 'deal', 'price', 'τιμή', 'σύγκριση', 'compare',
        'guide', 'οδηγός', 'how to', 'πως να', 'tutorial'
    ]

    NOISE_KEYWORDS = [
        'celebrity', 'gossip', 'scandal', 'πολιτική', 'politics',
        'έγκλημα', 'crime', 'accident', 'ατύχημα', 'breaking'
    ]

    HIGH_VALUE_NICHES = {
        'tech': ['laptop', 'phone', 'tablet', 'headphones', 'gadget'],
        'fitness': ['gym', 'workout', 'protein', 'weight', 'fitness'],
        'home': ['furniture', 'kitchen', 'cleaning', 'organization'],
        'finance': ['invest', 'crypto', 'stock', 'saving', 'money'],
        'education': ['course', 'learn', 'tutorial', 'certification']
    }

    def score(self, trend):
        keyword = trend['keyword'].lower()
        velocity = trend.get('velocity', 0)
        volume = trend.get('volume', 0)

        commercial_score = min(sum(0.5 for w in self.COMMERCIAL_KEYWORDS if w in keyword), 3)

        niche_score = 0
        for niche_keywords in self.HIGH_VALUE_NICHES.values():
            if any(w in keyword for w in niche_keywords):
                niche_score = 2
                break

        if velocity > 500:
            velocity_score = 3
        elif velocity > 300:
            velocity_score = 2
        elif velocity > 100:
            velocity_score = 1
        else:
            velocity_score = 0

        if volume > 10000:
            volume_score = 2
        elif volume > 1000:
            volume_score = 1
        else:
            volume_score = 0

        noise_penalty = sum(3 for w in self.NOISE_KEYWORDS if w in keyword)

        final_score = commercial_score + niche_score + velocity_score + volume_score - noise_penalty
        return round(max(0, min(10, final_score)), 2)

    def get_recommended_strategy(self, trend, score):
        keyword = trend['keyword'].lower()
        velocity = trend.get('velocity', 0)

        if score >= 8.5:
            if velocity > 400:
                return 'content_rush'
            elif any(w in keyword for w in ['buy', 'best', 'review']):
                return 'affiliate_article'
            else:
                return 'seo_content'
        elif score >= 6.5:
            return 'medium_post'
        else:
            return 'skip'
