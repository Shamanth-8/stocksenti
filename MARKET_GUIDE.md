# 🌍 Multi-Market Usage Guide

## ✅ **YES! You can analyze both US and Indian stock markets**

Your enhanced Financial News Sentiment Analyzer now supports both markets with dual API integration.

## 🇺🇸 **For US Companies - Use Finnhub (Recommended)**

### ✅ **What Works:**
- **Real-time data** (no delays)
- **Excellent coverage** of NYSE, NASDAQ stocks
- **60 API calls per minute** (vs NewsAPI's 100/day)
- **Automatic symbol lookup** (e.g., "Apple" → "AAPL")

### 📊 **Best US Companies to Try:**
- Apple (AAPL)
- Tesla (TSLA) 
- Microsoft (MSFT)
- Amazon (AMZN)
- Google (GOOGL)
- Meta (META)
- Netflix (NFLX)

### 🎯 **How to Use:**
1. Select "**finnhub**" in the sidebar
2. Enter company name: "**Apple**" or "**Tesla**"
3. Hit "🔍 Analyze Sentiment"

---

## 🇮🇳 **For Indian Companies - Use NewsAPI**

### ✅ **What Works:**
- **Global news coverage** including Indian sources
- **Major Indian companies** well covered
- **English language** financial news
- **Company name recognition** (e.g., "Reliance", "TCS")

### ⚠️ **Limitations:**
- **24-hour article delay** (free tier)
- **100 requests per day** limit
- **Development use only** (not for production)

### 📊 **Best Indian Companies to Try:**
- Reliance Industries
- Tata Consultancy Services (TCS)
- Infosys
- HDFC Bank
- Wipro
- ICICI Bank
- Bharti Airtel

### 🎯 **How to Use:**
1. Select "**newsapi**" in the sidebar  
2. Enter company name: "**Reliance**" or "**TCS**"
3. Hit "🔍 Analyze Sentiment"

---

## 🔑 **Your API Keys (Already Configured)**

```env
# NewsAPI - For Indian companies
NEWSAPI_KEY=d0713cc2f1a3404a92eda9cc2d76f453

# Finnhub - For US companies  
FINNHUB_API_KEY=d2u3869r01qo4hodslkgd2u3869r01qo4hodsll0
```

## 🚀 **Quick Start Examples**

### Example 1: Analyze Apple (US)
1. Switch to "**Finnhub**"
2. Enter "**Apple**" 
3. Get real-time sentiment analysis

### Example 2: Analyze Reliance (India)
1. Switch to "**NewsAPI**"
2. Enter "**Reliance**"
3. Get sentiment analysis (with 24h delay)

## 💡 **Pro Tips**

1. **For day trading**: Use Finnhub (US stocks only) for real-time data
2. **For research**: NewsAPI works well for both markets
3. **Mixed portfolio**: Switch between APIs based on the company
4. **Indian startups**: NewsAPI will have better coverage
5. **US tech stocks**: Finnhub provides superior data

## 🎯 **Expected Results**

- **Headlines**: 10-20 recent articles
- **Sentiment Analysis**: AI-powered classification (Positive/Negative/Neutral)
- **Confidence Scores**: How certain the AI is about each prediction
- **Visual Charts**: Pie charts and metrics for quick insights
- **Key Insights**: Most positive/negative headlines highlighted

## ⚡ **Performance**

- **Finnhub**: Instant results, real-time data
- **NewsAPI**: Slightly slower, but comprehensive coverage
- **AI Processing**: 2-3 seconds for sentiment analysis
- **Caching**: Results cached for improved performance

---

**🎉 Ready to analyze both markets! Your app is truly international now!**
