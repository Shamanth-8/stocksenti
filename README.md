# 📈 Financial News Sentiment Analyzer

A powerful Streamlit application that analyzes market sentiment from recent financial news using AI-powered sentiment analysis. Get real-time insights into how the market perceives your favorite companies!

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![HuggingFace](https://img.shields.io/badge/🤗_Hugging_Face-FFD21E?style=for-the-badge)

## ✨ Features

- **🔍 Real-time News Analysis**: Fetch the latest financial news from NewsAPI or Finnhub
- **🤖 AI-Powered Sentiment Detection**: Uses advanced transformer models from Hugging Face
- **📊 Interactive Visualizations**: Beautiful charts and metrics to understand sentiment trends
- **🎯 Company-Specific Analysis**: Search by company name or stock symbol
- **⚡ Fast & Responsive**: Cached results for improved performance
- **🌐 Easy Deployment**: Ready for Streamlit Cloud deployment

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- API key from either:
  - [NewsAPI.org](https://newsapi.org/register) (Free tier: 100 requests/day)
  - [Finnhub.io](https://finnhub.io/register) (Free tier: 60 calls/minute)

### Local Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd senti
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env with your API keys
   NEWSAPI_KEY=your_newsapi_key_here
   FINNHUB_API_KEY=your_finnhub_key_here
   NEWS_SOURCE=finnhub
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser** to `http://localhost:8501`

## 🌐 Deployment on Streamlit Cloud

### Step 1: Prepare Your Repository

1. **Push your code** to GitHub (make sure not to include .env or secrets.toml files)
2. **Update requirements.txt** if you've added any dependencies

### Step 2: Deploy on Streamlit Cloud

1. **Go to** [share.streamlit.io](https://share.streamlit.io)
2. **Connect your GitHub** account
3. **Select your repository** and branch
4. **Set the main file path**: `app.py`

### Step 3: Configure Secrets

1. **In Streamlit Cloud**, go to your app settings
2. **Add the following secrets**:
   ```toml
   NEWSAPI_KEY = "your_actual_newsapi_key"
   FINNHUB_API_KEY = "your_actual_finnhub_key"
   ```
3. **Save and deploy**

## 🛠️ Project Structure

```
senti/
├── app.py                    # Main Streamlit application
├── news_fetcher.py          # News API integration module
├── sentiment_analyzer.py    # Sentiment analysis module
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── README.md               # Project documentation
└── .streamlit/
    ├── config.toml         # Streamlit configuration
    └── secrets.toml.example # Secrets template
```

## 🔧 Configuration

### Environment Variables

- `NEWSAPI_KEY`: Your NewsAPI.org API key
- `FINNHUB_API_KEY`: Your Finnhub.io API key  
- `NEWS_SOURCE`: Preferred news source (`newsapi` or `finnhub`)

### API Limits

**NewsAPI (Free Tier)**:
- 100 requests per day
- Historical data limited to 1 month

**Finnhub (Free Tier)**:
- 60 API calls per minute
- Real-time data available
- Better for stock-specific news

## 📊 How It Works

1. **Input Processing**: Enter a company name or stock symbol
2. **News Fetching**: Retrieve recent news articles from your chosen API
3. **Sentiment Analysis**: Analyze each headline using Hugging Face transformers
4. **Visualization**: Display results with interactive charts and metrics
5. **Insights**: Get actionable insights about market sentiment

## 🤖 AI Model

This app uses the `cardiffnlp/twitter-roberta-base-sentiment-latest` model from Hugging Face, which is specifically trained for sentiment analysis and provides:

- **High Accuracy**: State-of-the-art transformer architecture
- **Fast Processing**: Optimized for real-time analysis
- **Robust Performance**: Handles various text formats and styles

## 🎨 Features in Detail

### Sentiment Metrics
- Overall sentiment classification (Positive/Negative/Neutral)
- Confidence scores for each prediction
- Distribution charts showing sentiment breakdown

### Interactive Visualizations
- Pie chart showing sentiment distribution
- Gauge chart for overall sentiment score
- Colored data tables with clickable links

### Smart Caching
- Results are cached to improve performance
- Automatic cache invalidation for fresh data

## 🔍 Usage Examples

### Analyzing Apple Inc.
```
Company Input: "Apple" or "AAPL"
Time Range: Last 7 days
Source: Finnhub
```

### Monitoring Tesla Sentiment
```
Company Input: "Tesla" or "TSLA" 
Time Range: Last 3 days
Source: NewsAPI
```

## 🚨 Troubleshooting

### Common Issues

1. **"No articles found"**
   - Try using the stock symbol instead of company name
   - Check if the company is publicly traded
   - Verify your API keys are correct

2. **"API key missing"**
   - Ensure your .env file is properly configured
   - For Streamlit Cloud, check your secrets configuration

3. **"Model loading failed"**
   - Check your internet connection
   - The model will download on first use (~500MB)

### Getting API Keys

**NewsAPI**:
1. Visit [newsapi.org/register](https://newsapi.org/register)
2. Sign up with your email
3. Copy your API key from the dashboard

**Finnhub**:
1. Visit [finnhub.io/register](https://finnhub.io/register)
2. Create a free account
3. Copy your API key from the dashboard

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) for the amazing web app framework
- [Hugging Face](https://huggingface.co/) for the transformer models
- [NewsAPI](https://newsapi.org/) for financial news data
- [Finnhub](https://finnhub.io/) for real-time financial data

---

**Made with ❤️ and 🤖 AI**
