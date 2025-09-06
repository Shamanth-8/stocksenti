import streamlit as st

# MUST be the very first Streamlit command!
st.set_page_config(
    page_title="Financial News Sentiment Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
from newsapi import NewsApiClient
from transformers import pipeline
import datetime
import os
from dotenv import load_dotenv
import finnhub
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Optional

# Load environment variables
load_dotenv()

# Initialize API clients
def get_api_key(key_name: str) -> str:
    """Get API key from environment variables or Streamlit secrets"""
    api_key = os.getenv(key_name, '')
    if not api_key:
        try:
            api_key = st.secrets.get(key_name, '')
        except:
            api_key = ''
    return api_key

newsapi_key = get_api_key('NEWSAPI_KEY')
finnhub_key = get_api_key('FINNHUB_API_KEY')

newsapi = None
finnhub_client = None

if newsapi_key:
    try:
        newsapi = NewsApiClient(api_key=newsapi_key)
    except Exception as e:
        st.warning(f"Failed to initialize NewsAPI: {e}")

if finnhub_key:
    try:
        finnhub_client = finnhub.Client(api_key=finnhub_key)
    except Exception as e:
        st.warning(f"Failed to initialize Finnhub: {e}")

# Initialize sentiment analysis pipeline
@st.cache_resource
def load_sentiment_pipeline():
    return pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")

sentiment_pipeline = load_sentiment_pipeline()

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sentiment-positive { color: #00C851; font-weight: bold; }
    .sentiment-negative { color: #FF4444; font-weight: bold; }
    .sentiment-neutral { color: #ffbb33; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# App title and description
st.markdown("<h1 class='main-header'>📈 Financial News Sentiment Analyzer</h1>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; margin-bottom: 2rem; color: #666;'>
    Analyze market sentiment from recent financial news using AI-powered sentiment analysis
</div>
""", unsafe_allow_html=True)

# Sidebar for input
st.sidebar.header("⚙️ Configuration")
company_name = st.sidebar.text_input(
    "Company Name or Stock Symbol", 
    placeholder="e.g., Apple, AAPL, Reliance, TCS, Infosys",
    help="Enter company name or stock symbol (works for US, Indian, and global companies)"
)

# Market selection hint
st.sidebar.info("💡 **Market Coverage:**\n" +
    "🇺🇸 **US**: Apple, Tesla, Microsoft, AAPL, TSLA\n" +
    "🇮🇳 **Indian**: Reliance, TCS, Infosys, Wipro, HDFC\n" +
    "🌍 **Global**: Works with major companies worldwide")

# News source selection
news_source = st.sidebar.selectbox(
    "News Source",
    ["finnhub", "newsapi"],
    index=0,  # Default to Finnhub (better for Indian stocks)
    help="Choose your preferred news API source"
)

num_articles = st.sidebar.slider("Number of Articles to Analyze", 5, 50, 20)
days_back = st.sidebar.slider(
    "Days to look back",
    min_value=1,
    max_value=30,
    value=7,
    help="Number of days to search for news articles"
)

# API key status
st.sidebar.subheader("📋 API Key Status")
if news_source == "newsapi":
    if newsapi_key:
        st.sidebar.success("✅ NewsAPI key configured")
        st.sidebar.warning("⚠️ NewsAPI Free Tier Limitations:")
        st.sidebar.info("• 100 requests/day\n• 24-hour article delay\n• Development use only")
    else:
        st.sidebar.error("❌ NewsAPI key missing")
        st.sidebar.info("Add NEWSAPI_KEY to your environment variables")
else:
    if finnhub_key:
        st.sidebar.success("✅ Finnhub API key configured")
        st.sidebar.info("📊 **Finnhub (Free tier):**\n• Real-time US stocks\n• 60 calls/minute\n• No Indian stocks (NSE/BSE)")
    else:
        st.sidebar.error("❌ Finnhub API key missing")
        st.sidebar.info("Add FINNHUB_API_KEY to your environment variables")

# Function to get company symbol for Finnhub
def get_company_symbol(company_name: str) -> Optional[str]:
    if not finnhub_client:
        return None
    
    # Note: Finnhub free tier doesn't support Indian exchanges (NSE/BSE)
    # For Indian companies, recommend using NewsAPI
    
    try:
        # Try direct symbol lookup
        search_results = finnhub_client.symbol_lookup(company_name)
        if search_results and 'result' in search_results:
            # Prefer US stocks first, then others
            us_stocks = [r for r in search_results['result'] if r.get('type') == 'Common Stock' and '.' not in r.get('symbol', '')]
            if us_stocks:
                return us_stocks[0].get('symbol')
            
            # Then try any common stock
            for result in search_results['result']:
                if result.get('type') == 'Common Stock':
                    return result.get('symbol')
        return None
    except Exception as e:
        st.warning(f"Could not find symbol for {company_name}: {e}")
        return None

# Function to fetch news from NewsAPI
def fetch_news_newsapi(company, num_articles, days_back):
    if not newsapi:
        return []
    try:
        from_date = (datetime.datetime.now() - datetime.timedelta(days=days_back)).strftime('%Y-%m-%d')
        # Enhanced search for Indian companies
        indian_terms = f'"{company} India" OR "{company} NSE" OR "{company} BSE"' if any(word in company.lower() for word in ['reliance', 'tcs', 'infosys', 'hdfc', 'wipro', 'icici', 'bharti', 'tata']) else ''
        search_query = f'"{company}" OR "{company} stock" OR "{company} shares" {indian_terms}'
        
        articles = newsapi.get_everything(
            q=search_query,
            from_param=from_date,
            language='en',
            sort_by='publishedAt',
            page_size=num_articles
        )
        return articles['articles'] if articles['status'] == 'ok' else []
    except Exception as e:
        st.error(f"Error fetching news from NewsAPI: {e}")
        return []

# Function to fetch news from Finnhub
def fetch_news_finnhub(company_symbol: str, num_articles: int, days_back: int):
    if not finnhub_client:
        return []
    try:
        to_date = datetime.datetime.now()
        from_date = to_date - datetime.timedelta(days=days_back)
        
        # Format dates as strings in YYYY-MM-DD format (Finnhub requirement)
        from_date_str = from_date.strftime('%Y-%m-%d')
        to_date_str = to_date.strftime('%Y-%m-%d')
        
        # Use string dates for the API call (not timestamps)
        news = finnhub_client.company_news(company_symbol, _from=from_date_str, to=to_date_str)
        articles = []
        for article in news[:num_articles]:
            if article.get('headline'):
                articles.append({
                    'title': article['headline'],
                    'description': article.get('summary', ''),
                    'url': article.get('url', ''),
                    'publishedAt': datetime.datetime.fromtimestamp(article['datetime']).isoformat(),
                    'source': {'name': article.get('source', 'Finnhub')}
                })
        return articles
    except Exception as e:
        st.error(f"Error fetching news from Finnhub: {e}")
        return []

# Main function to fetch news
def fetch_news(company, num_articles, source='newsapi', days_back=7):
    if source == 'finnhub' and finnhub_client:
        company_symbol = get_company_symbol(company)
        if company_symbol:
            return fetch_news_finnhub(company_symbol, num_articles, days_back)
        else:
            # Check if it might be an Indian company
            indian_companies = ['reliance', 'tcs', 'infosys', 'hdfc', 'wipro', 'icici', 'bharti', 'airtel', 'sbi', 'maruti']
            if any(word in company.lower() for word in indian_companies):
                st.warning(f"'{company}' appears to be an Indian company. Finnhub free tier doesn't support Indian exchanges. Please switch to NewsAPI for better coverage of Indian companies.")
            else:
                st.warning(f"Could not find stock symbol for '{company}'. Please try entering the stock symbol directly (e.g., AAPL for Apple).")
            return []
    elif source == 'newsapi' and newsapi:
        return fetch_news_newsapi(company, num_articles, days_back)
    else:
        st.error(f"No valid API configuration found for source: {source}")
        return []

# Function to analyze sentiment with better label mapping
def analyze_sentiment(headlines):
    if not headlines:
        return []
    
    results = sentiment_pipeline(headlines)
    processed_results = []
    
    for result in results:
        # Handle different label formats
        if isinstance(result, list):
            result = max(result, key=lambda x: x['score'])
        
        label = result['label'].upper()
        score = result['score']
        
        # Map labels to standard format
        label_mapping = {
            'LABEL_0': 'NEGATIVE',
            'LABEL_1': 'NEUTRAL', 
            'LABEL_2': 'POSITIVE',
            'NEGATIVE': 'NEGATIVE',
            'NEUTRAL': 'NEUTRAL',
            'POSITIVE': 'POSITIVE'
        }
        
        mapped_label = label_mapping.get(label, label)
        processed_results.append({
            'label': mapped_label,
            'score': score
        })
    
    return processed_results

# Function to create sentiment pie chart
def create_sentiment_pie_chart(sentiment_counts):
    labels = ['Positive', 'Negative', 'Neutral']
    values = [
        sentiment_counts.get('POSITIVE', 0),
        sentiment_counts.get('NEGATIVE', 0),
        sentiment_counts.get('NEUTRAL', 0)
    ]
    colors = ['#00C851', '#FF4444', '#ffbb33']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors),
        hole=0.4,
        textinfo='label+percent+value'
    )])
    
    fig.update_layout(
        title="Sentiment Distribution",
        showlegend=True,
        height=400
    )
    return fig

# Main app logic
analyze_button = st.sidebar.button("🔍 Analyze Sentiment", type="primary", use_container_width=True)

if analyze_button and company_name:
    # Check if required API key is available
    if news_source == "newsapi" and not newsapi_key:
        st.error("Please configure your NewsAPI key to continue.")
        st.stop()
    elif news_source == "finnhub" and not finnhub_key:
        st.error("Please configure your Finnhub API key to continue.")
        st.stop()
    
    # Show production warning for NewsAPI
    if news_source == "newsapi":
        st.warning("⚠️ **Development Mode**: Using NewsAPI free tier with 24-hour article delay. For production use, consider upgrading to NewsAPI Pro or using Finnhub.")
    
    with st.spinner("🔄 Fetching news and analyzing sentiment..."):
        # Fetch news articles
        articles = fetch_news(company_name, num_articles, news_source, days_back)
        
        if articles:
            # Extract headlines
            headlines = [article['title'] for article in articles]
            sources = [article['source']['name'] for article in articles]
            published_at = [article['publishedAt'] for article in articles]
            urls = [article['url'] for article in articles]
            
            # Analyze sentiment
            sentiment_results = analyze_sentiment(headlines)
            
            # Process results
            sentiments = []
            scores = []
            
            for result in sentiment_results:
                label = result['label']
                score = result['score']
                sentiments.append(label.title())
                scores.append(score)
            
            # Create DataFrame
            df = pd.DataFrame({
                'Headline': headlines,
                'Source': sources,
                'Published At': published_at,
                'Sentiment': sentiments,
                'Confidence': scores,
                'URL': urls
            })
            
            # Calculate overall sentiment
            sentiment_counts = df['Sentiment'].value_counts()
            total_articles = len(df)
            
            # Display results
            st.success(f"✅ Found {total_articles} articles for {company_name}")
            st.subheader(f"📊 Sentiment Overview for {company_name}")
            
            # Create columns for metrics
            col1, col2, col3, col4 = st.columns(4)
            
            # Calculate overall sentiment
            if len(sentiment_counts) > 0:
                dominant_sentiment = sentiment_counts.idxmax()
                avg_confidence = df['Confidence'].mean()
            else:
                dominant_sentiment = "Neutral"
                avg_confidence = 0
            
            with col1:
                sentiment_colors = {'Positive': '#00C851', 'Negative': '#FF4444', 'Neutral': '#ffbb33'}
                color = sentiment_colors.get(dominant_sentiment, '#6c757d')
                st.metric(
                    label="Overall Sentiment",
                    value=dominant_sentiment,
                    delta=f"{avg_confidence:.1%} confidence"
                )
                st.markdown(f"<div style='color: {color}; font-size: 2rem; text-align: center;'>●</div>", 
                           unsafe_allow_html=True)
            
            with col2:
                positive = sentiment_counts.get('Positive', 0)
                st.metric("Positive Articles", positive, 
                         f"{positive/total_articles*100:.1f}%")
            
            with col3:
                negative = sentiment_counts.get('Negative', 0)
                st.metric("Negative Articles", negative, 
                         f"{negative/total_articles*100:.1f}%")
            
            with col4:
                neutral = sentiment_counts.get('Neutral', 0)
                st.metric("Neutral Articles", neutral, 
                         f"{neutral/total_articles*100:.1f}%")
            
            # Display charts
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                # Pie chart
                fig = create_sentiment_pie_chart(sentiment_counts)
                st.plotly_chart(fig, use_container_width=True)
            
            with chart_col2:
                # Bar chart
                st.subheader("Sentiment Counts")
                sentiment_chart_data = pd.DataFrame({
                    'Sentiment': ['Positive', 'Neutral', 'Negative'],
                    'Count': [
                        sentiment_counts.get('Positive', 0),
                        sentiment_counts.get('Neutral', 0),
                        sentiment_counts.get('Negative', 0)
                    ]
                })
                st.bar_chart(sentiment_chart_data.set_index('Sentiment'))
            
            # Display headlines with sentiment
            st.subheader("Recent Headlines with Sentiment Analysis")
            
            # Color code based on sentiment
            def color_sentiment(sentiment):
                if sentiment == 'Positive':
                    return 'color: green'
                elif sentiment == 'Negative':
                    return 'color: red'
                else:
                    return 'color: gray'
            
            # Display styled dataframe
            styled_df = df[['Headline', 'Source', 'Sentiment', 'Confidence']].style.apply(
                lambda x: [color_sentiment(x['Sentiment'])] * len(x), 
                axis=1, subset=['Sentiment']
            )
            st.dataframe(styled_df, use_container_width=True)
            
            # Show most positive and negative headlines
            st.subheader("Key Insights")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Most Positive Headlines**")
                positive_news = df[df['Sentiment'] == 'Positive'].sort_values('Confidence', ascending=False)
                for _, row in positive_news.head(3).iterrows():
                    st.write(f"📈 {row['Headline']} ({(row['Confidence']*100):.1f}%)")
            
            with col2:
                st.write("**Most Negative Headlines**")
                negative_news = df[df['Sentiment'] == 'Negative'].sort_values('Confidence', ascending=False)
                for _, row in negative_news.head(3).iterrows():
                    st.write(f"📉 {row['Headline']} ({(row['Confidence']*100):.1f}%)")
            
            # Summary
            dominant_sentiment = sentiment_counts.idxmax() if not sentiment_counts.empty else "Neutral"
            st.subheader("Overall Market Sentiment")
            if dominant_sentiment == "Positive":
                st.success(f"✅ The overall market sentiment for {company_name} is **Positive**")
            elif dominant_sentiment == "Negative":
                st.error(f"❌ The overall market sentiment for {company_name} is **Negative**")
            else:
                st.info(f"ℹ️ The overall market sentiment for {company_name} is **Neutral**")
                
        else:
            if news_source == "newsapi":
                st.warning("No articles found for this company. This might be due to NewsAPI's free tier limitations (24-hour delay, limited sources). Try a more popular company name or consider using Finnhub.")
            else:
                st.warning("No articles found for this company. Please try a different company name or stock symbol.")

# Show welcome information when no company is entered
elif not company_name:
    # Welcome message
    st.info("👈 Enter a company name or stock symbol in the sidebar to get started!")
    
    # Feature highlights
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🔍 **Real-time Analysis**
        Get up-to-date sentiment analysis from the latest financial news articles
        """)
    
    with col2:
        st.markdown("""
        ### 🤖 **AI-Powered**
        Uses advanced Hugging Face transformer models for accurate sentiment detection
        """)
    
    with col3:
        st.markdown("""
        ### 📊 **Global Coverage**
        Supports US, Indian, and international stock markets
        """)
    
    # Market coverage information
    st.subheader("🌍 Supported Markets")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **🇺🇸 United States:**
        - Apple (AAPL)
        - Tesla (TSLA)
        - Microsoft (MSFT)
        - Amazon (AMZN)
        - Google (GOOGL)
        - Meta (META)
        - Netflix (NFLX)
        """)
    
    with col2:
        st.markdown("""
        **🇮🇳 India:**
        - Reliance Industries
        - Tata Consultancy Services (TCS)
        - Infosys
        - HDFC Bank
        - Wipro
        - ICICI Bank
        - Bharti Airtel
        """)
    
    # Sample companies to try
    st.subheader("💡 Try These Popular Companies")
    
    # US Companies
    st.write("🇺🇸 **US Companies:**")
    us_companies = ["Apple", "Tesla", "Microsoft", "Amazon", "Google"]
    cols = st.columns(len(us_companies))
    for i, company in enumerate(us_companies):
        with cols[i]:
            if st.button(company, key=f"us_{company}"):
                st.rerun()
    
    # Indian Companies  
    st.write("🇮🇳 **Indian Companies:**")
    indian_companies = ["Reliance", "TCS", "Infosys", "HDFC Bank", "Wipro"]
    cols = st.columns(len(indian_companies))
    for i, company in enumerate(indian_companies):
        with cols[i]:
            if st.button(company, key=f"indian_{company}"):
                st.rerun()
    
    # API comparison
    st.subheader("⚙️ Choose the Right API for Your Market")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("""
        **🇮🇳 For Indian Companies (use NewsAPI):**
        ✅ Global news coverage
        ✅ Covers Indian companies well
        ✅ Major Indian companies included
        ❌ 24-hour delay (free tier)
        ❌ 100 requests/day limit
        """)
    
    with col2:
        st.success("""
        **🇺🇸 For US Companies (use Finnhub):**
        ✅ Real-time data
        ✅ Excellent for US stocks (NYSE, NASDAQ)
        ✅ 60 calls/minute
        ✅ Stock symbol lookup
        ❌ No Indian stocks on free tier
        """)

# Add instructions in sidebar
st.sidebar.markdown("---")
st.sidebar.info("""
**How to use:**
1. Enter a public company name
2. Adjust the number of articles to analyze
3. Click 'Analyze Sentiment' or press Enter
4. View the sentiment analysis results
""")

# Add note about API key
st.sidebar.markdown("---")
st.sidebar.caption("""
Note: You need a NewsAPI key to use this app. 
Add it to a .env file as NEWSAPI_KEY=your_key_here
""")