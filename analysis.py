def run_analysis(keyword, period):
    posts = fetch_all(keyword, period)
    return format_output(posts)

def fetch_all(keyword, period):
    print(f"Fetching for keyword={keyword}, period={period}")
    reddit_posts = fetch_reddit(keyword, period)
    print(f"Reddit: {len(reddit_posts)} posts")
    rss_posts = fetch_rss(keyword, period)
    print(f"RSS: {len(rss_posts)} posts")
    gnews_posts = fetch_gnews(keyword, period)
    print(f"GNews: {len(gnews_posts)} posts")
    newsapi_posts = fetch_newsapi(keyword, period)
    print(f"NewsAPI: {len(newsapi_posts)} posts")

    all_posts = reddit_posts + rss_posts + gnews_posts + newsapi_posts
    print(f"Total combined posts: {len(all_posts)}")

    all_posts = sorted(all_posts, key=lambda x: x['influence_score'], reverse=True)
    return all_posts


import praw
from datetime import datetime, timedelta

def fetch_reddit(keyword, period, max_posts=20):
    """
    Fetch posts from Reddit safely.
    Handles authentication errors, network issues, and limits results.
    """
    try:
        reddit = praw.Reddit(
            client_id="YOUR_CLIENT_ID",
            client_secret="YOUR_CLIENT_SECRET",
            user_agent="trending-topic-app"
        )
    except Exception as e:
        print(f"❌ Reddit client error: {e}")
        return []

    # Calculate start time
    now = datetime.utcnow()
    if period == "Day":
        start_time = now - timedelta(days=1)
    elif period == "Week":
        start_time = now - timedelta(weeks=1)
    elif period == "Month":
        start_time = now - timedelta(days=30)
    elif period == "Year":
        start_time = now - timedelta(days=365)
    else:
        start_time = now

    posts = []
    try:
        # Search popular subreddits
        subreddits = ['all', 'worldnews', 'technology', 'news']
        for subreddit in subreddits:
            for submission in reddit.subreddit(subreddit).search(keyword, sort='new', limit=50):
                post_time = datetime.utcfromtimestamp(submission.created_utc)
                if post_time < start_time:
                    continue
                posts.append({
                    "title": submission.title,
                    "url": submission.url,
                    "source": "Reddit",
                    "published": str(post_time),
                    "influence_score": submission.score
                })
                if len(posts) >= max_posts:
                    break
            if len(posts) >= max_posts:
                break
    except praw.exceptions.PRAWException as e:
        print(f"❌ Reddit fetch error (PRAWException): {e}")
    except Exception as e:
        print(f"❌ Reddit fetch error: {e}")

    print(f"✅ Reddit fetched {len(posts)} posts")
    return posts


import feedparser
from datetime import datetime, timedelta

RSS_FEEDS = {
    "NDTV":"https://feeds.feedburner.com/ndtvnews-top-stories",
    "The Hindu":"https://www.thehindu.com/news/national/?service=rss",
    "Times of India":"https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
    "BBC":"http://feeds.bbci.co.uk/news/rss.xml",
    "CNN":"http://rss.cnn.com/rss/edition.rss"
    # add more feeds if needed
}

def fetch_rss(keyword, period, max_per_feed=5):
    start_time = datetime.utcnow()
    if period == "Day":
        start_time -= timedelta(days=1)
    elif period == "Week":
        start_time -= timedelta(weeks=1)
    elif period == "Month":
        start_time -= timedelta(days=30)
    elif period == "Year":
        start_time -= timedelta(days=365)

    posts = []
    for source_name, feed_url in RSS_FEEDS.items():
        feed = feedparser.parse(feed_url)
        count = 0
        for entry in feed.entries:
            if count >= max_per_feed:
                break
            try:
                pub_date = datetime(*entry.published_parsed[:6])
            except:
                continue
            if pub_date < start_time:
                continue
            if keyword.lower() in entry.title.lower():
                posts.append({
                    "title": entry.title,
                    "url": entry.link,
                    "source": source_name,
                    "published": str(pub_date),
                    "influence_score": len(entry.title)
                })
                count += 1
    print(f"✅ RSS fetched {len(posts)} posts")
    return posts


import requests
from datetime import datetime, timedelta

GNEWS_API_KEY = "YOUR_GNEWS_API_KEY"  # Replace with your real key

def fetch_gnews(keyword, period, max_posts=25):
    # Determine start time
    start_time = datetime.utcnow()
    if period == "Day":
        start_time -= timedelta(days=1)
    elif period == "Week":
        start_time -= timedelta(weeks=1)
    elif period == "Month":
        start_time -= timedelta(days=30)
    elif period == "Year":
        start_time -= timedelta(days=365)

    url = f"https://gnews.io/api/v4/search?q={keyword}&lang=en&sortby=publishedAt&max=50&apikey={GNEWS_API_KEY}"
    posts = []

    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 401:
            print("❌ GNews Unauthorized — check your API key")
            return []
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        print(f"❌ GNews fetch error: {e}")
        return []

    for a in data.get("articles", []):
        try:
            pub_date = datetime.strptime(a['publishedAt'], "%Y-%m-%dT%H:%M:%SZ")
        except:
            continue
        if pub_date < start_time:
            continue
        posts.append({
            "title": a['title'],
            "url": a['url'],
            "source": a['source']['name'],
            "published": str(pub_date),
            "influence_score": 0
        })
        if len(posts) >= max_posts:
            break

    print(f"✅ GNews fetched {len(posts)} posts")
    return posts


import requests
from datetime import datetime, timedelta

NEWSAPI_KEY = "YOUR_NEWSAPI_KEY"  # Replace with your real key

def fetch_newsapi(keyword, period, max_posts=25):
    # Determine start time
    start_time = datetime.utcnow()
    if period == "Day":
        start_time -= timedelta(days=1)
    elif period == "Week":
        start_time -= timedelta(weeks=1)
    elif period == "Month":
        start_time -= timedelta(days=30)
    elif period == "Year":
        start_time -= timedelta(days=365)

    url = f"https://newsapi.org/v2/everything?q={keyword}&language=en&sortBy=publishedAt&pageSize=100&apiKey={NEWSAPI_KEY}"
    posts = []

    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 401:
            print("❌ NewsAPI Unauthorized — check your API key")
            return []
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        print(f"❌ NewsAPI fetch error: {e}")
        return []

    for a in data.get("articles", []):
        try:
            pub_date = datetime.strptime(a['publishedAt'], "%Y-%m-%dT%H:%M:%SZ")
        except:
            continue
        if pub_date < start_time:
            continue
        posts.append({
            "title": a['title'],
            "url": a['url'],
            "source": a['source']['name'],
            "published": str(pub_date),
            "influence_score": 0
        })
        if len(posts) >= max_posts:
            break

    print(f"✅ NewsAPI fetched {len(posts)} posts")
    return posts


import json

def format_output(posts):
    return json.dumps(posts, indent=2)


def format_output(posts):
    if not posts:
        return "<b>No trending posts found.</b>"

    html = """
    <div style="font-family: Arial, sans-serif; max-width: 800px; margin: auto;">
        <h2 style="color:#333;">🧠 Trending Topics</h2>
        <div style="margin-bottom: 20px;">
    """

    for i, p in enumerate(posts[:20], start=1):
        html += f"""
        <div style="padding:10px; margin-bottom:10px; border:1px solid #ddd; border-radius:8px; box-shadow:1px 1px 5px #eee;">
            <h4 style="margin:0;"><a href="{p['url']}" target="_blank" style="text-decoration:none; color:#0077b6;">{i}. {p['title']}</a></h4>
            <p style="margin:5px 0; font-size:0.9em; color:#555;">
                Source: <b>{p['source']}</b> | Published: {p.get('published', 'N/A')} | Influence Score: {p.get('influence_score', 0)}
            </p>
        </div>
        """

    html += "</div></div>"
    return html
