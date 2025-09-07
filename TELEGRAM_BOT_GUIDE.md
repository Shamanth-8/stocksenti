# 🤖 Telegram Financial Sentiment Bot Guide

## 🎉 **Your Bot is Live!**

**Bot Username:** @Blackbuck_bot  **

## 🚀 **Quick Start**

### 1. **Find Your Bot**
- Open Telegram
- Search for `@Blackbuck_bot`
- Click "Start" or send `/start`

### 2. **Basic Commands**
```
/start     - Welcome message and quick actions
/help      - Show all available commands  
/analyze   - Analyze sentiment for any company
/examples  - Show example companies to try
```

### 3. **Analyze a Company**
Just send: `/analyze Apple` or `/analyze Reliance`

## 📱 **How to Use**

### **Option 1: Commands**
```
/analyze Tesla
/analyze Reliance
/analyze Microsoft
```

### **Option 2: Direct Text**
Just type the company name:
```
Apple
Tesla
Reliance Industries
```

### **Option 3: Interactive Buttons**
Use the buttons that appear when you send `/start`

## 🌍 **Supported Markets**

| Market | Best For | Examples |
|--------|----------|----------|
| **🇺🇸 US** | Real-time data | Apple, Tesla, Microsoft, Amazon |
| **🇮🇳 India** | Major companies | Reliance, TCS, Infosys, HDFC Bank |
| **🌐 Global** | International firms | Samsung, Toyota, Nestlé |

## 📊 **What You Get**

When you analyze a company, the bot provides:

### **📈 Sentiment Analysis**
- Overall sentiment (Positive/Negative/Neutral)
- Confidence percentage
- Detailed breakdown of articles

### **📰 Key Insights**
- Most positive headlines
- Most negative headlines  
- Article count and sources

### **⚡ Real-time Updates**
- Live progress updates during analysis
- Smart API selection (Finnhub for US, NewsAPI for Indian companies)

## 🎯 **Example Conversations**

### **Analyzing Apple:**
```
You: /analyze Apple
Bot: 🔍 Analyzing sentiment for Apple...
     📊 Using Finnhub for US stock coverage...
     📊 Symbol: AAPL
     ⏳ Fetching real-time articles...
     📰 Found 15 articles
     🤖 Running AI sentiment analysis...
     
     🤖 Sentiment Analysis Results
     
     Company: Apple
     API Source: Finnhub  
     Articles Analyzed: 15
     
     📈 Overall Sentiment: POSITIVE 🟢
     Confidence: 78.4%
     
     📊 Breakdown:
     • 📈 Positive: 9 (60.0%)
     • 📉 Negative: 3 (20.0%) 
     • 📊 Neutral: 3 (20.0%)
```

### **Analyzing Reliance:**
```
You: /analyze Reliance
Bot: 🔍 Analyzing sentiment for Reliance...
     📰 Using NewsAPI for Indian company coverage...
     ⏳ Fetching articles...
     📰 Found 12 articles
     🤖 Running AI sentiment analysis...
     
     [Similar detailed results...]
```

## 🔧 **Advanced Features**

### **Interactive Buttons**
- 🔄 Analyze Another - Quick restart
- 📊 Detailed View - More insights
- ⚙️ Settings - Configuration

### **Smart Company Detection**
The bot automatically detects:
- US companies → Uses Finnhub (real-time)
- Indian companies → Uses NewsAPI (comprehensive)
- Stock symbols → Auto-converts (AAPL, TSLA, etc.)

### **Progress Updates**
Real-time status updates:
- 🔎 Looking up stock symbol...
- ⏳ Fetching articles...
- 🤖 Running AI analysis...

## 💡 **Pro Tips**

1. **For US Stocks:** Use company names or symbols
   - `Apple` or `AAPL` ✅
   - `Tesla` or `TSLA` ✅

2. **For Indian Companies:** Use full company names
   - `Reliance Industries` ✅
   - `Tata Consultancy Services` ✅

3. **Quick Access:** 
   - Just type company name (no need for `/analyze`)
   - Use buttons for faster navigation

4. **Best Results:**
   - Popular companies work best
   - Recent IPOs might have limited data
   - Check examples with `/examples`

## 🚨 **Troubleshooting**

### **"No articles found"**
- Try using the stock symbol (AAPL instead of Apple)
- For Indian companies, switch to NewsAPI coverage
- Check if the company is publicly traded

### **Slow responses**
- AI analysis takes 10-20 seconds
- Finnhub might timeout occasionally
- Bot shows progress updates

### **API Limitations**
- NewsAPI: 100 requests/day, 24h article delay
- Finnhub: 60 requests/minute, US stocks only

## 🔄 **Running the Bot**

### **Start the Bot:**
```powershell
python telegram_bot.py
```

### **Keep it Running:**
The bot needs to stay running to respond to messages. You'll see:
```
INFO - NewsAPI initialized successfully
INFO - Finnhub initialized successfully  
INFO - Sentiment analysis model loaded successfully
INFO - Starting Telegram bot...
INFO - Application started
```

### **For Production:**
Consider using:
- **PM2** (Process Manager)
- **Screen/Tmux** (Terminal multiplexer)
- **Cloud hosting** (AWS, Heroku, etc.)

## 📈 **Usage Statistics**

From the logs, your bot successfully:
- ✅ Connected to Telegram API
- ✅ Processed multiple user requests
- ✅ Analyzed companies (Apple, Tesla, etc.)
- ✅ Generated sentiment analysis results
- ✅ Handled interactive buttons
- ✅ Ran for extended periods

## 🎯 **Next Steps**

1. **Share your bot:** Send `@Blackbuck_bot` to friends
2. **Test different companies:** Try both US and Indian stocks
3. **Explore features:** Use all the interactive buttons
4. **Monitor performance:** Check the console logs
5. **Deploy to cloud:** For 24/7 availability

## 🛡️ **Security Notes**

- ✅ Bot token is configured
- ✅ API keys are secured
- ✅ Error handling implemented  
- ✅ User input validation active

## 🎉 **Your Bot is Ready!**

Your Telegram bot **@Blackbuck_bot** is fully functional with:

🤖 **AI-Powered Analysis** - Advanced sentiment detection  
🌍 **Global Coverage** - US, Indian, and international markets  
⚡ **Real-time Data** - Live news and instant analysis  
📱 **User-Friendly** - Simple commands and interactive buttons  
🔄 **Always Available** - 24/7 sentiment analysis (when running)

**Start chatting with @Blackbuck_bot now!** 🚀
