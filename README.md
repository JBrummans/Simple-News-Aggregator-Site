# Simple-News-Aggregator-Site

This is a simple Python project to generate a static website aggregating news from multiple sources (RSS feeds and Hacker News). The goal is to stay informed without falling into endless scrolling on news or social media sites.

## Features

- Aggregates news from any number of RSS feeds (configured in `.env`)
- Includes top stories from Hacker News
- Fully static HTML output (no backend required to serve)
- Dark theme for comfortable reading
- Easy to add/remove feeds via `.env` file
- Customizable article limit

## Requirements

- Python 3.10+
- pip

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/Simple-News-Aggregator-Site.git
   cd Simple-News-Aggregator-Site
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   If `requirements.txt` does not exist, install manually:
   ```bash
   pip install requests feedparser jinja2 python-dotenv beautifulsoup4
   ```

3. **Configure your feeds:**

   Edit the `.env` file to set your article limit and RSS feeds:
   ```
   ARTICLE_LIMIT=15
   LOBSTERS_RSS=https://lobste.rs/rss
   REDDIT_SELFHOSTED_RSS=https://old.reddit.com/r/selfhosted/top/.rss?t=day
   REDDIT_TECHNOLOGY_RSS=https://old.reddit.com/r/technology/top/.rss?t=day
   # Add more feeds as needed, using *_RSS as the key
   ```

## Usage

Run the aggregator script to generate your static HTML file:

```bash
python aggregator.py --output-file index.html
```

- The default output is `index.html` in the project directory.
- Open `index.html` in your browser to view your news dashboard.

## Customization

- **Adding/Removing Feeds:**  
  Just add or remove lines ending with `_RSS` in your `.env` file. No code changes needed.
- **Article Limit:**  
  Change `ARTICLE_LIMIT` in `.env` to control how many articles per feed are shown.
- **Theme:**  
  The site uses a dark theme by default. You can edit `template.html` for further customization.

## Project Structure

```
.
├── aggregator.py      # Main script to fetch and render news
├── template.html      # Jinja2 template for HTML output
├── .env               # Configuration for feeds and article limit
├── README.md          # This file
└── requirements.txt   # Python dependencies (optional)
```

## License

MIT License

---

*This project was created to help avoid doomscrolling while staying up to date with tech and news!*
