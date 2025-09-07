import os
import logging
from typing import Dict, Any
import datetime
import asyncio
from dotenv import load_dotenv

# Telegram bot imports
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Our existing functionality
from newsapi import NewsApiClient
from transformers import pipeline
import finnhub
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class FinancialSentimentBot:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.newsapi_key = os.getenv('NEWSAPI_KEY')
        self.finnhub_key = os.getenv('FINNHUB_API_KEY')
        
        # Initialize API clients
        self.newsapi = None
        self.finnhub_client = None
        self.sentiment_pipeline = None
        
        # User preferences storage
        self.user_preferences = {}
        
        self._initialize_apis()
    
    def _initialize_apis(self):
        """Initialize all APIs and models"""
        try:
            # Initialize NewsAPI
            if self.newsapi_key:
                self.newsapi = NewsApiClient(api_key=self.newsapi_key)
                logger.info("NewsAPI initialized successfully")
            
            # Initialize Finnhub
            if self.finnhub_key:
                self.finnhub_client = finnhub.Client(api_key=self.finnhub_key)
                logger.info("Finnhub initialized successfully")
            
            # Initialize sentiment analysis model
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis", 
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            logger.info("Sentiment analysis model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error initializing APIs: {e}")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🤖 **Financial Sentiment Analyzer Bot**

Welcome! I can analyze market sentiment for both US and Indian companies using AI-powered sentiment analysis.

**🌍 What I can do:**
• Analyze sentiment for US stocks (Apple, Tesla, Microsoft, etc.)
• Analyze sentiment for Indian companies (Reliance, TCS, Infosys, etc.)  
• Provide real-time sentiment analysis
• Generate beautiful charts and insights

**📋 Commands:**
/help - Show all commands
/analyze <company> - Analyze sentiment for a company
/settings - Change API preferences
/examples - Show example companies to try

**🚀 Quick Start:**
Just type: `/analyze Apple` or `/analyze Reliance`

Let's get started! 📈
        """
        
        # Create inline keyboard for quick actions
        keyboard = [
            [InlineKeyboardButton("🇺🇸 Analyze US Stock", callback_data="quick_us")],
            [InlineKeyboardButton("🇮🇳 Analyze Indian Stock", callback_data="quick_indian")],
            [InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
            [InlineKeyboardButton("❓ Help", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
**🤖 Financial Sentiment Analyzer - Help**

**📋 Available Commands:**
• `/start` - Welcome message and quick actions
• `/analyze <company>` - Analyze sentiment for any company
• `/settings` - Change API source preferences
• `/examples` - Show example companies
• `/help` - Show this help message

**💡 Usage Examples:**
• `/analyze Apple` - Analyze Apple Inc.
• `/analyze TSLA` - Analyze Tesla using stock symbol
• `/analyze Reliance` - Analyze Reliance Industries
• `/analyze TCS` - Analyze Tata Consultancy Services

**🌍 Supported Markets:**
🇺🇸 **US Stocks:** Apple, Tesla, Microsoft, Amazon, Google, Meta, Netflix
🇮🇳 **Indian Companies:** Reliance, TCS, Infosys, HDFC Bank, Wipro, ICICI

**⚙️ API Sources:**
• **Finnhub** - Best for US stocks (real-time data)
• **NewsAPI** - Best for Indian companies (global coverage)

**📊 What You Get:**
• Sentiment analysis of recent headlines
• Overall sentiment score (Positive/Negative/Neutral)
• Confidence levels
• Key insights and most impactful news
• Visual charts (coming soon!)

Need help? Just ask! 🚀
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def examples_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /examples command"""
        examples_text = """
**💡 Example Companies to Try**

**🇺🇸 US Companies (Use Finnhub):**
• `/analyze Apple` - Apple Inc. 
• `/analyze Tesla` - Tesla Motors
• `/analyze Microsoft` - Microsoft Corp
• `/analyze Amazon` - Amazon.com
• `/analyze Google` - Alphabet/Google
• `/analyze NVDA` - NVIDIA (by symbol)

**🇮🇳 Indian Companies (Use NewsAPI):**
• `/analyze Reliance` - Reliance Industries
• `/analyze TCS` - Tata Consultancy Services
• `/analyze Infosys` - Infosys Ltd
• `/analyze HDFC Bank` - HDFC Bank
• `/analyze Wipro` - Wipro Technologies
• `/analyze ICICI` - ICICI Bank

**🔥 Trending Examples:**
• `/analyze Bitcoin` - Cryptocurrency news
• `/analyze OpenAI` - AI company news
• `/analyze SpaceX` - Space industry news

**💡 Pro Tips:**
• Use company names or stock symbols
• Try both US and Indian companies
• Check different time periods with settings

Ready to analyze? Pick any company! 📈
        """
        
        # Quick action buttons
        keyboard = [
            [InlineKeyboardButton("🍎 Try Apple", callback_data="example_apple")],
            [InlineKeyboardButton("🚗 Try Tesla", callback_data="example_tesla")],
            [InlineKeyboardButton("💼 Try Reliance", callback_data="example_reliance")],
            [InlineKeyboardButton("💻 Try TCS", callback_data="example_tcs")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(examples_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    def get_company_symbol(self, company_name: str) -> str:
        """Get company stock symbol using Finnhub"""
        if not self.finnhub_client:
            return company_name
        
        try:
            search_results = self.finnhub_client.symbol_lookup(company_name)
            if search_results and 'result' in search_results:
                # Prefer US stocks first
                us_stocks = [r for r in search_results['result'] 
                           if r.get('type') == 'Common Stock' and '.' not in r.get('symbol', '')]
                if us_stocks:
                    return us_stocks[0].get('symbol', company_name)
                
                # Then try any common stock
                for result in search_results['result']:
                    if result.get('type') == 'Common Stock':
                        return result.get('symbol', company_name)
            
            return company_name
        except Exception as e:
            logger.error(f"Error in symbol lookup: {e}")
            return company_name
    
    def fetch_news_finnhub(self, company_symbol: str, days_back: int = 7) -> list:
        """Fetch news from Finnhub"""
        if not self.finnhub_client:
            return []
        
        try:
            to_date = datetime.datetime.now()
            from_date = to_date - datetime.timedelta(days=days_back)
            from_date_str = from_date.strftime('%Y-%m-%d')
            to_date_str = to_date.strftime('%Y-%m-%d')
            
            news = self.finnhub_client.company_news(company_symbol, _from=from_date_str, to=to_date_str)
            
            articles = []
            for article in news[:20]:  # Limit to 20 articles
                if article.get('headline'):
                    articles.append({
                        'title': article['headline'],
                        'description': article.get('summary', ''),
                        'url': article.get('url', ''),
                        'publishedAt': datetime.datetime.fromtimestamp(article['datetime']).isoformat(),
                        'source': article.get('source', 'Finnhub')
                    })
            
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching news from Finnhub: {e}")
            return []
    
    def fetch_news_newsapi(self, company_name: str, days_back: int = 7) -> list:
        """Fetch news from NewsAPI"""
        if not self.newsapi:
            return []
        
        try:
            from_date = (datetime.datetime.now() - datetime.timedelta(days=days_back)).strftime('%Y-%m-%d')
            
            # Enhanced search for Indian companies
            indian_companies = ['reliance', 'tcs', 'infosys', 'hdfc', 'wipro', 'icici', 'bharti', 'tata']
            indian_terms = f' OR "{company_name} India" OR "{company_name} NSE" OR "{company_name} BSE"' if any(word in company_name.lower() for word in indian_companies) else ''
            search_query = f'"{company_name}" OR "{company_name} stock" OR "{company_name} shares"{indian_terms}'
            
            articles = self.newsapi.get_everything(
                q=search_query,
                from_param=from_date,
                language='en',
                sort_by='publishedAt',
                page_size=20
            )
            
            if articles['status'] == 'ok':
                return [{
                    'title': article['title'],
                    'description': article['description'] or '',
                    'url': article['url'],
                    'publishedAt': article['publishedAt'],
                    'source': article['source']['name']
                } for article in articles['articles'] if article['title']]
            
            return []
            
        except Exception as e:
            logger.error(f"Error fetching news from NewsAPI: {e}")
            return []
    
    def analyze_sentiment(self, texts: list) -> list:
        """Analyze sentiment of texts"""
        if not texts or not self.sentiment_pipeline:
            return []
        
        try:
            results = self.sentiment_pipeline(texts)
            processed_results = []
            
            for result in results:
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
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return []
    
    def calculate_overall_sentiment(self, sentiment_results: list) -> dict:
        """Calculate overall sentiment metrics"""
        if not sentiment_results:
            return {
                'overall_sentiment': 'NEUTRAL',
                'confidence': 0.0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'total_articles': 0
            }
        
        positive_count = sum(1 for r in sentiment_results if r['label'] == 'POSITIVE')
        negative_count = sum(1 for r in sentiment_results if r['label'] == 'NEGATIVE')
        neutral_count = sum(1 for r in sentiment_results if r['label'] == 'NEUTRAL')
        
        total_articles = len(sentiment_results)
        
        # Determine overall sentiment
        if positive_count > negative_count:
            overall_sentiment = 'POSITIVE'
        elif negative_count > positive_count:
            overall_sentiment = 'NEGATIVE'
        else:
            overall_sentiment = 'NEUTRAL'
        
        # Calculate average confidence
        avg_confidence = sum(r['score'] for r in sentiment_results) / total_articles
        
        return {
            'overall_sentiment': overall_sentiment,
            'confidence': avg_confidence,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'total_articles': total_articles
        }
    
    async def analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /analyze command"""
        if not context.args:
            await update.message.reply_text(
                "Please provide a company name!\n\n"
                "**Usage:** `/analyze <company>`\n"
                "**Examples:** `/analyze Apple` or `/analyze Reliance`",
                parse_mode='Markdown'
            )
            return
        
        company_name = ' '.join(context.args)
        user_id = update.effective_user.id
        
        # Send initial message
        status_message = await update.message.reply_text(
            f"🔍 **Analyzing sentiment for {company_name}...**\n\n"
            "⏳ Fetching recent news articles...",
            parse_mode='Markdown'
        )
        
        try:
            # Determine best API source
            indian_companies = ['reliance', 'tcs', 'infosys', 'hdfc', 'wipro', 'icici', 'bharti', 'airtel', 'sbi', 'maruti']
            use_newsapi = any(word in company_name.lower() for word in indian_companies)
            
            # Fetch news
            if use_newsapi:
                await status_message.edit_text(
                    f"🔍 **Analyzing {company_name}**\n\n"
                    "📰 Using NewsAPI for Indian company coverage...\n"
                    "⏳ Fetching articles...",
                    parse_mode='Markdown'
                )
                articles = self.fetch_news_newsapi(company_name)
                api_used = "NewsAPI"
            else:
                await status_message.edit_text(
                    f"🔍 **Analyzing {company_name}**\n\n"
                    "📊 Using Finnhub for US stock coverage...\n"
                    "🔎 Looking up stock symbol...",
                    parse_mode='Markdown'
                )
                company_symbol = self.get_company_symbol(company_name)
                await status_message.edit_text(
                    f"🔍 **Analyzing {company_name}**\n\n"
                    f"📊 Symbol: {company_symbol}\n"
                    "⏳ Fetching real-time articles...",
                    parse_mode='Markdown'
                )
                articles = self.fetch_news_finnhub(company_symbol)
                api_used = "Finnhub"
            
            if not articles:
                await status_message.edit_text(
                    f"❌ **No articles found for {company_name}**\n\n"
                    f"API used: {api_used}\n\n"
                    "**Try:**\n"
                    "• Different company name\n"
                    "• Stock symbol (e.g., AAPL for Apple)\n"
                    "• /examples for suggested companies",
                    parse_mode='Markdown'
                )
                return
            
            # Analyze sentiment
            await status_message.edit_text(
                f"🔍 **Analyzing {company_name}**\n\n"
                f"📰 Found {len(articles)} articles\n"
                "🤖 Running AI sentiment analysis...",
                parse_mode='Markdown'
            )
            
            headlines = [article['title'] for article in articles]
            sentiment_results = self.analyze_sentiment(headlines)
            overall_sentiment = self.calculate_overall_sentiment(sentiment_results)
            
            # Prepare results
            sentiment_emoji = {
                'POSITIVE': '📈',
                'NEGATIVE': '📉',
                'NEUTRAL': '📊'
            }
            
            sentiment_color = {
                'POSITIVE': '🟢',
                'NEGATIVE': '🔴',
                'NEUTRAL': '🟡'
            }
            
            # Generate result message
            result_message = f"""
🤖 **Sentiment Analysis Results**

**Company:** {company_name}
**API Source:** {api_used}
**Articles Analyzed:** {overall_sentiment['total_articles']}

{sentiment_emoji[overall_sentiment['overall_sentiment']]} **Overall Sentiment:** {overall_sentiment['overall_sentiment']} {sentiment_color[overall_sentiment['overall_sentiment']]}
**Confidence:** {overall_sentiment['confidence']:.1%}

📊 **Breakdown:**
• 📈 Positive: {overall_sentiment['positive_count']} ({overall_sentiment['positive_count']/overall_sentiment['total_articles']*100:.1f}%)
• 📉 Negative: {overall_sentiment['negative_count']} ({overall_sentiment['negative_count']/overall_sentiment['total_articles']*100:.1f}%)
• 📊 Neutral: {overall_sentiment['neutral_count']} ({overall_sentiment['neutral_count']/overall_sentiment['total_articles']*100:.1f}%)

**💡 Key Insights:**
            """
            
            # Add most positive and negative headlines
            df = pd.DataFrame([
                {
                    'headline': articles[i]['title'],
                    'sentiment': sentiment_results[i]['label'],
                    'confidence': sentiment_results[i]['score']
                }
                for i in range(min(len(articles), len(sentiment_results)))
            ])
            
            if len(df[df['sentiment'] == 'POSITIVE']) > 0:
                most_positive = df[df['sentiment'] == 'POSITIVE'].nlargest(1, 'confidence')
                result_message += f"\n📈 **Most Positive:** {most_positive.iloc[0]['headline'][:100]}..."
            
            if len(df[df['sentiment'] == 'NEGATIVE']) > 0:
                most_negative = df[df['sentiment'] == 'NEGATIVE'].nlargest(1, 'confidence')
                result_message += f"\n📉 **Most Negative:** {most_negative.iloc[0]['headline'][:100]}..."
            
            result_message += f"\n\n⏰ Analysis completed at {datetime.datetime.now().strftime('%H:%M:%S')}"
            
            # Create action buttons
            keyboard = [
                [InlineKeyboardButton("🔄 Analyze Another", callback_data="analyze_another")],
                [InlineKeyboardButton("📊 Detailed View", callback_data=f"details_{company_name}")],
                [InlineKeyboardButton("⚙️ Settings", callback_data="settings")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await status_message.edit_text(result_message, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in analyze_command: {e}")
            await status_message.edit_text(
                f"❌ **Error analyzing {company_name}**\n\n"
                f"Error: {str(e)}\n\n"
                "Please try again or contact support.",
                parse_mode='Markdown'
            )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "quick_us":
            await query.edit_message_text(
                "🇺🇸 **US Stock Analysis**\n\n"
                "Enter a US company name:\n"
                "Example: `Apple`, `Tesla`, `Microsoft`\n\n"
                "Or try: /analyze Apple",
                parse_mode='Markdown'
            )
        
        elif query.data == "quick_indian":
            await query.edit_message_text(
                "🇮🇳 **Indian Stock Analysis**\n\n"
                "Enter an Indian company name:\n"
                "Example: `Reliance`, `TCS`, `Infosys`\n\n"
                "Or try: /analyze Reliance",
                parse_mode='Markdown'
            )
        
        elif query.data.startswith("example_"):
            company = query.data.split("_")[1].title()
            # Simulate analyze command
            context.args = [company]
            await self.analyze_command(update, context)
        
        elif query.data == "help":
            await self.help_command(update, context)
        
        elif query.data == "analyze_another":
            await query.edit_message_text(
                "🔍 **Ready for another analysis!**\n\n"
                "Use: `/analyze <company_name>`\n\n"
                "**Quick examples:**\n"
                "• `/analyze Apple`\n"
                "• `/analyze Tesla`\n"
                "• `/analyze Reliance`\n"
                "• `/analyze TCS`",
                parse_mode='Markdown'
            )
    
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages"""
        text = update.message.text.strip()
        
        # If user just types a company name, analyze it
        if len(text.split()) <= 3 and not text.startswith('/'):
            context.args = text.split()
            await update.message.reply_text(
                f"🔍 Analyzing '{text}'...\n"
                "💡 Tip: Use `/analyze {text}` for faster results next time!",
                parse_mode='Markdown'
            )
            await self.analyze_command(update, context)
        else:
            await update.message.reply_text(
                "👋 Hi! I'm your Financial Sentiment Analyzer bot.\n\n"
                "**To analyze a company:**\n"
                "`/analyze <company_name>`\n\n"
                "**Examples:**\n"
                "• `/analyze Apple`\n"
                "• `/analyze Reliance`\n\n"
                "Type `/help` for more commands!",
                parse_mode='Markdown'
            )
    
    def run(self):
        """Start the bot"""
        if not self.bot_token:
            logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
            return
        
        # Create application
        application = Application.builder().token(self.bot_token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("examples", self.examples_command))
        application.add_handler(CommandHandler("analyze", self.analyze_command))
        application.add_handler(CallbackQueryHandler(self.button_callback))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler))
        
        # Start the bot
        logger.info("Starting Telegram bot...")
        application.run_polling()

if __name__ == '__main__':
    bot = FinancialSentimentBot()
    bot.run()
