# Options Trading Learning Guide with Alpaca API

A comprehensive, code-based learning system for understanding options trading using the Alpaca API.

## 🎯 Who Is This For?

- Programmers who want to learn options trading
- Traders who learn better through code than theory
- Anyone with Alpaca API access who wants hands-on practice
- Complete beginners to options (programming experience assumed)

## 📦 What's Included?

### 1. `options_learning_guide.py` - THE BASICS
**Start here!** This is your foundation.

Covers:
- ✅ Lesson 1: Understanding the Options Chain
- ✅ Lesson 2: Call Options (betting stocks go UP)
- ✅ Lesson 3: Put Options (betting stocks go DOWN)
- ✅ Lesson 4: ITM vs ATM vs OTM (moneyness)
- ✅ Lesson 5: Time Decay (Theta - the silent killer)

**Run it:** `python options_learning_guide.py`

Each lesson is interactive and uses REAL market data from Alpaca!

### 2. `advanced_options_trading.py` - LEVEL UP
**After mastering basics**, move here.

Covers:
- 📊 The Greeks (Delta, Gamma, Theta, Vega)
- 💰 Covered Call Strategy (generate income)
- 🛡️ Protective Put Strategy (portfolio insurance)
- 🎮 Paper Trading Examples (actual trade execution)
- ⚠️ Risk Management (THE MOST IMPORTANT)

**Run it:** `python advanced_options_trading.py`

Choose individual lessons or run them all!

### 3. `options_scanner.py` - PRACTICAL TOOLS
**When you're ready to find opportunities**

Features:
- 🔍 High IV Scanner (find selling opportunities)
- 🔍 Low IV Scanner (find buying opportunities)
- 📈 Options Chain Analyzer (deep dive any stock)
- 📰 Earnings Play Analyzer (understand the risks!)
- 📖 Quick Reference Guide (cheat sheet)

**Run it:** `python options_scanner.py`

Scans real market data and gives strategy recommendations!

## 🚀 Setup Instructions

### Prerequisites

1. **Python 3.8+** installed
2. **Alpaca Account** (free paper trading account)
   - Sign up at: https://alpaca.markets
   - Enable options trading in account settings
   - Get your API keys

### Installation

```bash
# 1. Install required packages
pip install alpaca-py pandas

# 2. Set your API keys as environment variables
# On Mac/Linux:
export APCA_API_KEY_ID="your_key_here"
export APCA_API_SECRET_KEY="your_secret_here"

# On Windows (Command Prompt):
set APCA_API_KEY_ID=your_key_here
set APCA_API_SECRET_KEY=your_secret_here

# On Windows (PowerShell):
$env:APCA_API_KEY_ID="your_key_here"
$env:APCA_API_SECRET_KEY="your_secret_here"

# 3. Run the basic learning guide
python options_learning_guide.py
```

### Alternative: Add Keys to Script

You can also modify the scripts to include your keys directly (less secure):

```python
trading_client = TradingClient(
    api_key="YOUR_KEY_HERE",
    secret_key="YOUR_SECRET_HERE",
    paper=True
)
```

## 📚 Recommended Learning Path

### Week 1: Foundations
1. ✅ Run `options_learning_guide.py` 
2. ✅ Complete all 5 lessons
3. ✅ Take notes on what confuses you
4. ✅ Re-run lessons until concepts click
5. ✅ Use real examples (SPY, AAPL, etc.)

**Goal:** Understand calls, puts, strikes, and expiration

### Week 2: Advanced Concepts
1. ✅ Run `advanced_options_trading.py`
2. ✅ Study the Greeks (especially Delta and Theta)
3. ✅ Learn covered calls and protective puts
4. ✅ Place paper trades (no real money!)
5. ✅ Track your paper trades

**Goal:** Understand how Greeks affect option prices

### Week 3-4: Practice & Strategy
1. ✅ Use `options_scanner.py` to find opportunities
2. ✅ Analyze 5-10 different stocks' option chains
3. ✅ Paper trade different strategies
4. ✅ Keep a trading journal
5. ✅ Review what worked and what didn't

**Goal:** Develop your trading plan

### Month 2-3: Paper Trading
1. ✅ Paper trade consistently (3-5 trades/week)
2. ✅ Try different strategies
3. ✅ Focus on risk management
4. ✅ Track ALL trades in a spreadsheet
5. ✅ Aim for consistent results

**Goal:** Prove you can be profitable with fake money

### Month 4+: Real Money (IF READY)
1. ⚠️ Start with TINY positions (1% of portfolio max)
2. ⚠️ Only trade strategies you've mastered
3. ⚠️ Keep strict risk management
4. ⚠️ Continue learning and adapting
5. ⚠️ Don't quit your day job!

**Goal:** Transition to real trading (if profitable in paper)

## ⚠️ CRITICAL WARNINGS

### 1. Options Can Lose 100% of Value
Unlike stocks, options can (and often do) expire worthless. Only invest money you can afford to lose completely.

### 2. Paper Trade First - SERIOUSLY
Don't skip this step! Minimum 1-3 months of paper trading. Most people lose money at first.

### 3. Risk Management Is Everything
- Never risk more than 1-2% per trade
- Always know your max loss BEFORE entering
- Set stop losses
- Don't revenge trade

### 4. IV Crush Is Real
Buying options before earnings? You can be right about direction and still lose money due to IV crush.

### 5. Time Decay Never Sleeps
Options lose value every day (theta decay). This accelerates near expiration.

### 6. Greeks Matter
Don't trade without understanding Delta, Gamma, Theta, and Vega. They determine option behavior.

## 🔥 Common Beginner Mistakes

1. ❌ Buying weekly options (too much theta decay)
2. ❌ Buying options right before earnings (IV crush)
3. ❌ Not taking profits (greed)
4. ❌ Not cutting losses (hope)
5. ❌ Trading illiquid options (wide spreads)
6. ❌ Selling naked options (unlimited risk)
7. ❌ Overleveraging (too many contracts)
8. ❌ Ignoring the Greeks
9. ❌ Not having a plan
10. ❌ Skipping paper trading

## 📊 Recommended Resources

### Free Learning
- **TastyTrade** - tastytrade.com (excellent free videos)
- **OptionAlpha** - optionalpha.com (strategy guides)
- **Alpaca Docs** - docs.alpaca.markets/docs/options-trading
- **Reddit** - r/options (community, but verify everything!)

### Tools
- **Options Profit Calculator** - optionsprofitcalculator.com
- **Market Chameleon** - marketchameleon.com (IV data)
- **TradingView** - tradingview.com (charts)
- **Alpaca Paper Trading** - Free practice account

### Books (Optional)
- "Options as a Strategic Investment" by Lawrence McMillan
- "Option Volatility and Pricing" by Sheldon Natenberg
- "The Options Playbook" by Brian Overby (free online!)

## 🤝 Getting Help

### If Code Doesn't Work
1. Check API keys are set correctly
2. Verify options trading is enabled in Alpaca account
3. Make sure you're using paper=True
4. Check market is open (options don't trade 24/7)
5. Try with liquid symbols like SPY, QQQ, AAPL

### If Concepts Don't Click
1. Re-run the lessons multiple times
2. Try with different stocks
3. Draw out the P/L diagrams on paper
4. Watch YouTube videos on the specific concept
5. Paper trade to see it in action

### Common Issues

**"No options found"**
- Options trading might not be enabled on your Alpaca account
- Symbol might not have options (try SPY, AAPL, MSFT)
- Market might be closed

**"Authentication failed"**
- Check your API keys
- Make sure environment variables are set
- Try hardcoding keys temporarily to test

**"Data not available"**
- Market might be closed
- Symbol might be invalid
- Try with SPY (always has data)

## 💡 Pro Tips

1. **Start with SPY** - Most liquid options market, tight spreads, always active
2. **Trade during market hours** - Better fills, real-time data
3. **Check the bid/ask spread** - Should be <10% of option price
4. **Give yourself time** - Buy options 30+ days out minimum
5. **Take screenshots** - Document your learning journey
6. **Keep a journal** - Write down why you entered each trade
7. **Review regularly** - What worked? What didn't? Why?
8. **Stay small** - Better to make $10 correctly than lose $1000
9. **Avoid the news** - Focus on price action and strategy
10. **Be patient** - Options trading takes 6-12 months to learn properly

## 🎓 Learning Objectives

By the end of this course, you should be able to:

- ✅ Explain the difference between calls and puts
- ✅ Understand strike prices and expiration dates
- ✅ Calculate breakeven points
- ✅ Identify ITM, ATM, and OTM options
- ✅ Explain all four Greeks and their impact
- ✅ Execute basic strategies (covered calls, protective puts)
- ✅ Use Alpaca API to fetch and analyze options
- ✅ Assess risk before entering any trade
- ✅ Recognize common pitfalls and avoid them
- ✅ Make informed decisions about whether options are right for you

## 🚨 Final Reminder

**Options trading is risky.** You can lose 100% of your investment. This guide is educational only - not financial advice. 

**Never trade with money you can't afford to lose.**

Paper trade for at least 1-3 months before using real money. Most traders lose money at first. Be part of the minority that learns properly before risking capital.

Good luck, and remember: **PAPER TRADE FIRST!**

---

## 📝 Quick Start Commands

```bash
# Basic lessons (start here)
python options_learning_guide.py

# Advanced concepts
python advanced_options_trading.py

# Scanner and tools
python options_scanner.py
```

## 📞 Support

For Alpaca API issues: https://alpaca.markets/support
For learning questions: Review the code comments - they're extensive!

---

**Version:** 1.0  
**Last Updated:** 2024  
**License:** Educational Use Only  
**Disclaimer:** Not financial advice. Trade at your own risk.