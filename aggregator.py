import requests
import feedparser
from jinja2 import Environment, FileSystemLoader
from datetime import datetime, timezone
from operator import itemgetter
import html
from bs4 import BeautifulSoup
import argparse

# --- 1. Data Retrieval Functions ---

def fetch_hacker_news(limit=15):
    """Fetches top Hacker News stories using the official API."""
    hn_data = []
    try:
        # Get the IDs of the top stories
        top_story_ids = requests.get('https://hacker-news.firebaseio.com/v0/topstories.json').json()

        # Fetch details for the first 'limit' stories
        for i, story_id in enumerate(top_story_ids[:limit]):
            story_url = f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json'
            story = requests.get(story_url).json()

            # Skip stories without a URL or that are 'ask' or 'job' posts without text
            if story and story.get('url') and story.get('title'):
                # Convert HN time (Unix timestamp) to a datetime object
                post_time = datetime.fromtimestamp(story.get('time', 0), tz=timezone.utc)
                
                hn_data.append({
                    'source': 'Hacker News',
                    'title': story['title'],
                    'link': story['url'],
                    'description': f"{story.get('score', 0)} points, by {story.get('by', 'anon')}",
                    'time_posted': post_time,
                    'display_time': post_time.strftime('%Y-%m-%d %H:%M:%S UTC')
                })
    except Exception as e:
        print(f"Error fetching Hacker News: {e}")
    return hn_data

def fetch_rss_feed(url, source_name, limit=15):
    """
    Fetches and parses an RSS feed, with special handling for Mastodon titles 
    and stripping images from the description.
    """
    feed_data = []
    try:
        feed = feedparser.parse(url)
        
        # Check for feed-level errors
        if feed.get('bozo') == 1 and feed.get('bozo_exception'):
            print(f"Warning: RSS feed for {source_name} is malformed: {feed.bozo_exception}")

        for entry in feed.entries[:limit]:
            
            post_time = datetime.now(timezone.utc)
            if hasattr(entry, 'published_parsed'):
                post_time = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            
            post_title = getattr(entry, 'title', 'No Title')
            
            # Special logic for Mastodon
            # if source_name == 'Mastodon.au' and post_title in ('No Title', ''):
            #     if hasattr(entry, 'author_detail') and entry.author_detail.get('name'):
            #         author_name = entry.author_detail.get('name')
            #         post_title = f"Post by {author_name.strip()}"
            #     else:
            #         post_title = f"Mastodon Post ({post_time.strftime('%H:%M')})"

            raw_description = getattr(entry, 'summary', getattr(entry, 'description', 'No description available'))
            soup = BeautifulSoup(raw_description, 'html.parser')
            
            # Find and remove all <img> tags from the HTML structure
            for img in soup.find_all('img'):
                img.decompose() # .decompose() removes the tag and its contents entirely
                
            # Convert the cleaned soup back to a string
            description = str(soup)
            
            # If the output is wrapped in an outer tag (like <div> or <p>), extract its inner HTML
            # This helps keep the rendered output clean
            if soup.body and len(soup.body.contents) == 1:
                description = str(soup.body.contents[0])


            feed_data.append({
                'source': source_name,
                'title': post_title,
                'link': getattr(entry, 'link', '#'),
                # 'description': description,
                'time_posted': post_time,
                'display_time': post_time.strftime('%Y-%m-%d %H:%M:%S UTC')
            })
            
    except Exception as e:
        print(f"Error fetching {source_name}: {e}")
        
    return feed_data

def aggregate_and_render(output_file='index.html'):
    """Combines all feeds, sorts, and generates the HTML output."""
    all_news = []

    # Get data from all sources
    all_news.extend(fetch_hacker_news(limit=15))
    all_news.extend(fetch_rss_feed('https://lobste.rs/rss', 'Lobsters', limit=15))
    # all_news.extend(fetch_rss_feed('https://mastodon.au/tags/news.rss', 'Mastodon', limit=15))
    all_news.extend(fetch_rss_feed('https://www.abc.net.au/news/feed/2942460/rss.xml', 'ABC', limit=15))
    all_news.extend(fetch_rss_feed('https://old.reddit.com/r/selfhosted/top/.rss?t=day', 'r/selfhosted', limit=15))
    all_news.extend(fetch_rss_feed('https://old.reddit.com/r/technology/top/.rss?t=day', 'r/technology', limit=15))

    # Sort all entries by time_posted, descending (newest first)
    all_news.sort(key=itemgetter('time_posted'), reverse=True)

    # Setup Jinja2 environment and load template
    # Note: Jinja2 looks for the template relative to the script's execution, which is fine here.
    env = Environment(loader=FileSystemLoader('.')) 
    template = env.get_template('template.html')

    # Render the template with the combined data
    html_output = template.render(
        news_items=all_news,
        generated_at=datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    )

    # Save the HTML file to the specified location
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_output)

    print(f"Successfully generated HTML file at: {output_file}")

if __name__ == '__main__':
    # Setup argument parser
    parser = argparse.ArgumentParser(description="A Python script to aggregate news feeds and generate a static HTML file.")
    parser.add_argument(
        '--output-file',
        type=str,
        default='index.html',
        help="The path and filename for the output HTML file. Default is 'index.html'."
    )
    args = parser.parse_args()
    
    # Pass the argument to the main function
    aggregate_and_render(output_file=args.output_file)
