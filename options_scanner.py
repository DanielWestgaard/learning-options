"""
Options Scanner and Analyzer
=============================

This tool helps you scan and analyze options to find trading opportunities.
It includes:
1. High IV (Implied Volatility) Scanner - for selling premium
2. Low IV Scanner - for buying options cheap
3. Options Chain Analyzer - detailed analysis of any stock
4. Earnings Play Analyzer - be careful with IV crush!
"""

import os
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOptionContractsRequest
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta
import pandas as pd
from collections import defaultdict

# Initialize clients
trading_client = TradingClient(
    api_key=os.getenv('APCA_API_KEY_ID'),
    secret_key=os.getenv('APCA_API_SECRET_KEY'),
    paper=True
)

stock_data_client = StockHistoricalDataClient(
    api_key=os.getenv('APCA_API_KEY_ID'),
    secret_key=os.getenv('APCA_API_SECRET_KEY')
)


def get_stock_price(symbol):
    """Get current stock price."""
    try:
        quote = stock_data_client.get_stock_latest_quote(
            StockLatestQuoteRequest(symbol_or_symbols=symbol)
        )[symbol]
        return (quote.ask_price + quote.bid_price) / 2
    except:
        return None


def calculate_iv_rank(symbol, days=30):
    """
    Calculate IV Rank (where current IV sits vs historical range).
    This is a simplified version - real IV rank needs options data.
    We'll use stock volatility as a proxy.
    """
    try:
        end = datetime.now()
        start = end - timedelta(days=days * 3)  # Get more data for comparison
        
        request = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Day,
            start=start,
            end=end
        )
        
        bars = stock_data_client.get_stock_bars(request)[symbol]
        
        if not bars or len(bars) < 20:
            return None
        
        # Calculate daily returns
        closes = [bar.close for bar in bars]
        returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
        
        # Current volatility (last 30 days)
        recent_vol = pd.Series(returns[-days:]).std() * (252 ** 0.5) * 100
        
        # Historical volatility range
        all_vol = pd.Series(returns).std() * (252 ** 0.5) * 100
        
        # Simplified IV rank (actual would use options IV)
        return min(100, max(0, (recent_vol / all_vol) * 100))
        
    except:
        return None


def scan_high_iv_opportunities(symbols, min_price=5, max_price=500):
    """
    Scan for high IV opportunities - good for SELLING options.
    
    High IV = High premiums = Good for sellers
    """
    print(f"\n{'='*80}")
    print("HIGH IV SCANNER - Opportunities to SELL Premium")
    print(f"{'='*80}\n")
    print("Scanning for stocks with elevated volatility...")
    print("These are good candidates for selling covered calls or cash-secured puts.\n")
    
    results = []
    
    for symbol in symbols:
        try:
            price = get_stock_price(symbol)
            if not price or price < min_price or price > max_price:
                continue
            
            iv_rank = calculate_iv_rank(symbol)
            if not iv_rank or iv_rank < 50:  # Looking for high IV
                continue
            
            # Get some options to check
            expiry_date = (datetime.now() + timedelta(days=45)).strftime('%Y-%m-%d')
            
            request = GetOptionContractsRequest(
                underlying_symbols=[symbol],
                expiration_date_gte=datetime.now().strftime('%Y-%m-%d'),
                expiration_date_lte=expiry_date,
                type='call',
                limit=10
            )
            
            options = trading_client.get_option_contracts(request).option_contracts
            
            if options:
                # Find ATM option
                atm_option = min(options, key=lambda x: abs(x.strike_price - price))
                
                results.append({
                    'symbol': symbol,
                    'price': price,
                    'iv_rank': iv_rank,
                    'atm_strike': atm_option.strike_price,
                    'expiry': atm_option.expiration_date
                })
            
        except Exception as e:
            continue
    
    if not results:
        print("No high IV opportunities found in the scanned symbols.")
        return
    
    # Sort by IV rank
    results.sort(key=lambda x: x['iv_rank'], reverse=True)
    
    print(f"{'Symbol':<10} {'Price':<12} {'IV Rank':<12} {'Strategy Idea'}")
    print("-" * 80)
    
    for r in results[:10]:  # Top 10
        strategy = "Covered Call" if r['price'] < 200 else "Cash-Secured Put"
        print(f"{r['symbol']:<10} ${r['price']:<11.2f} {r['iv_rank']:<11.1f}% {strategy}")
    
    print("\n" + "="*80)
    print("INTERPRETATION:")
    print("="*80)
    print("""
IV Rank > 75%: VERY HIGH - Excellent for selling premium
IV Rank 50-75%: HIGH - Good for selling premium
IV Rank 25-50%: MEDIUM - Neutral
IV Rank < 25%: LOW - Better for buying options

Strategy for High IV:
1. Covered Calls: Own 100 shares, sell OTM calls
2. Cash-Secured Puts: Sell OTM puts, keep cash to buy if assigned
3. Credit Spreads: Sell options, buy further OTM for protection
""")


def scan_low_iv_opportunities(symbols, min_price=10, max_price=300):
    """
    Scan for low IV opportunities - good for BUYING options.
    
    Low IV = Cheap premiums = Good for buyers (before a move)
    """
    print(f"\n{'='*80}")
    print("LOW IV SCANNER - Opportunities to BUY Options")
    print(f"{'='*80}\n")
    print("Scanning for stocks with low volatility...")
    print("These could be good for buying options IF you expect a move.\n")
    
    results = []
    
    for symbol in symbols:
        try:
            price = get_stock_price(symbol)
            if not price or price < min_price or price > max_price:
                continue
            
            iv_rank = calculate_iv_rank(symbol)
            if not iv_rank or iv_rank > 50:  # Looking for low IV
                continue
            
            # Get some options
            expiry_date = (datetime.now() + timedelta(days=45)).strftime('%Y-%m-%d')
            
            request = GetOptionContractsRequest(
                underlying_symbols=[symbol],
                expiration_date_gte=datetime.now().strftime('%Y-%m-%d'),
                expiration_date_lte=expiry_date,
                type='call',
                limit=10
            )
            
            options = trading_client.get_option_contracts(request).option_contracts
            
            if options:
                atm_option = min(options, key=lambda x: abs(x.strike_price - price))
                
                results.append({
                    'symbol': symbol,
                    'price': price,
                    'iv_rank': iv_rank,
                    'atm_strike': atm_option.strike_price,
                    'expiry': atm_option.expiration_date
                })
            
        except:
            continue
    
    if not results:
        print("No low IV opportunities found in the scanned symbols.")
        return
    
    results.sort(key=lambda x: x['iv_rank'])
    
    print(f"{'Symbol':<10} {'Price':<12} {'IV Rank':<12} {'Strategy Idea'}")
    print("-" * 80)
    
    for r in results[:10]:
        strategy = "Long Call/Put" if r['iv_rank'] < 25 else "Debit Spread"
        print(f"{r['symbol']:<10} ${r['price']:<11.2f} {r['iv_rank']:<11.1f}% {strategy}")
    
    print("\n" + "="*80)
    print("INTERPRETATION:")
    print("="*80)
    print("""
Low IV = Cheap options, but for a reason!
Stock might be quiet/boring right now.

Good times to buy low IV:
1. Before expected catalysts (earnings, FDA approval, etc.)
2. Technical breakout forming
3. Major news pending
4. Market overreaction to downside

WARNING: Low IV can stay low!
Don't just buy because it's "cheap" - need a reason to expect movement.
""")


def analyze_options_chain(symbol, days_to_expiry=30):
    """
    Detailed analysis of an options chain for a specific stock.
    """
    print(f"\n{'='*80}")
    print(f"OPTIONS CHAIN ANALYSIS: {symbol}")
    print(f"{'='*80}\n")
    
    # Get stock info
    price = get_stock_price(symbol)
    if not price:
        print(f"Could not get price for {symbol}")
        return
    
    print(f"Current Price: ${price:.2f}")
    
    iv_rank = calculate_iv_rank(symbol)
    if iv_rank:
        print(f"IV Rank (approx): {iv_rank:.1f}%")
        if iv_rank > 75:
            print("Status: VERY HIGH IV - Good for selling")
        elif iv_rank > 50:
            print("Status: HIGH IV - Good for selling")
        elif iv_rank < 25:
            print("Status: LOW IV - Good for buying")
        else:
            print("Status: MEDIUM IV - Neutral")
    
    print("\n" + "-"*80)
    
    # Get options
    expiry_date = (datetime.now() + timedelta(days=days_to_expiry)).strftime('%Y-%m-%d')
    
    # Get calls
    call_request = GetOptionContractsRequest(
        underlying_symbols=[symbol],
        expiration_date_gte=datetime.now().strftime('%Y-%m-%d'),
        expiration_date_lte=expiry_date,
        type='call',
        limit=100
    )
    
    calls = trading_client.get_option_contracts(call_request).option_contracts
    
    # Get puts
    put_request = GetOptionContractsRequest(
        underlying_symbols=[symbol],
        expiration_date_gte=datetime.now().strftime('%Y-%m-%d'),
        expiration_date_lte=expiry_date,
        type='put',
        limit=100
    )
    
    puts = trading_client.get_option_contracts(put_request).option_contracts
    
    if not calls and not puts:
        print("No options available for this symbol.")
        return
    
    # Organize by expiration
    expirations = set()
    for opt in calls + puts:
        expirations.add(opt.expiration_date)
    
    expirations = sorted(expirations)
    
    print(f"\nAvailable Expirations:")
    for i, exp in enumerate(expirations[:5], 1):
        days_away = (exp - datetime.now().date()).days
        print(f"  {i}. {exp} ({days_away} days)")
    
    if not expirations:
        return
    
    # Analyze first expiration
    exp = expirations[0]
    exp_calls = [c for c in calls if c.expiration_date == exp]
    exp_puts = [p for p in puts if p.expiration_date == exp]
    
    exp_calls.sort(key=lambda x: x.strike_price)
    exp_puts.sort(key=lambda x: x.strike_price)
    
    print(f"\nDetailed Chain for {exp} ({(exp - datetime.now().date()).days} days):")
    print("-" * 80)
    
    # Find key strikes
    atm_call = min(exp_calls, key=lambda x: abs(x.strike_price - price)) if exp_calls else None
    atm_put = min(exp_puts, key=lambda x: abs(x.strike_price - price)) if exp_puts else None
    
    print(f"\n{'Type':<10} {'Strike':<12} {'Moneyness':<15} {'Symbol'}")
    print("-" * 80)
    
    # Show calls around current price
    for call in exp_calls:
        distance = call.strike_price - price
        pct = (distance / price) * 100
        
        if abs(distance) < price * 0.15:  # Within 15% of current price
            if distance < -5:
                moneyness = f"ITM -{abs(pct):.1f}%"
            elif abs(distance) < 2:
                moneyness = f"ATM"
            else:
                moneyness = f"OTM +{pct:.1f}%"
            
            print(f"CALL       ${call.strike_price:<10.2f}  {moneyness:<15} {call.symbol}")
    
    print()
    
    # Show puts around current price
    for put in exp_puts:
        distance = price - put.strike_price
        pct = (distance / price) * 100
        
        if abs(distance) < price * 0.15:
            if distance < -5:
                moneyness = f"ITM -{abs(pct):.1f}%"
            elif abs(distance) < 2:
                moneyness = f"ATM"
            else:
                moneyness = f"OTM +{pct:.1f}%"
            
            print(f"PUT        ${put.strike_price:<10.2f}  {moneyness:<15} {put.symbol}")
    
    # Strategy recommendations
    print("\n" + "="*80)
    print("STRATEGY RECOMMENDATIONS:")
    print("="*80)
    
    if iv_rank and iv_rank > 60:
        print(f"""
Given HIGH IV ({iv_rank:.1f}%):

BULLISH:
  • Sell OTM puts (${atm_put.strike_price - (price * 0.05):.2f} strike)
  • Sell covered calls if you own shares
  
BEARISH:
  • Sell OTM calls (if you're willing to own at lower prices)
  • Buy puts but be aware of high premium
  
NEUTRAL:
  • Sell iron condors (sell both OTM call and put)
  • Sell strangles for premium collection
""")
    
    elif iv_rank and iv_rank < 40:
        print(f"""
Given LOW IV ({iv_rank:.1f}%):

BULLISH:
  • Buy calls (${atm_call.strike_price:.2f} or ${atm_call.strike_price + (price * 0.05):.2f} strike)
  • Bull call spreads (buy ATM, sell OTM)
  
BEARISH:
  • Buy puts (${atm_put.strike_price:.2f} or ${atm_put.strike_price - (price * 0.05):.2f} strike)
  • Bear put spreads (buy ATM, sell OTM)
  
NEUTRAL:
  • Wait for better setup
  • Consider longer-dated options
""")
    
    else:
        print("""
MEDIUM IV - Balanced conditions

Consider:
  • Directional plays if you have strong conviction
  • Spreads to reduce cost
  • Longer-dated options to reduce theta impact
""")


def earnings_play_analyzer(symbol):
    """
    Special analyzer for earnings plays.
    
    WARNING: Earnings = High IV = IV Crush after announcement!
    """
    print(f"\n{'='*80}")
    print(f"EARNINGS PLAY ANALYZER: {symbol}")
    print(f"{'='*80}\n")
    
    print("⚠️  WARNING: Earnings plays are VERY risky!")
    print("=" * 80)
    
    price = get_stock_price(symbol)
    if not price:
        print(f"Could not get price for {symbol}")
        return
    
    print(f"\nCurrent Price: ${price:.2f}")
    
    # Get options before and after typical earnings date
    before_earnings = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    after_earnings = (datetime.now() + timedelta(days=45)).strftime('%Y-%m-%d')
    
    # Get near-term options
    request_near = GetOptionContractsRequest(
        underlying_symbols=[symbol],
        expiration_date_gte=datetime.now().strftime('%Y-%m-%d'),
        expiration_date_lte=before_earnings,
        type='call',
        limit=50
    )
    
    # Get longer-term options
    request_far = GetOptionContractsRequest(
        underlying_symbols=[symbol],
        expiration_date_gte=before_earnings,
        expiration_date_lte=after_earnings,
        type='call',
        limit=50
    )
    
    near_options = trading_client.get_option_contracts(request_near).option_contracts
    far_options = trading_client.get_option_contracts(request_far).option_contracts
    
    print("\n" + "="*80)
    print("EARNINGS PLAY STRATEGIES:")
    print("="*80)
    
    print("""
1. STRADDLE (Buy Call + Put at same strike)
   ═══════════════════════════════════════════
   • Profit if stock makes BIG move (either direction)
   • Loss if stock doesn't move enough
   • Needs to move > premium paid
   
   Risk: IV CRUSH after earnings
   Even if you're right on direction, you can lose money!

2. STRANGLE (Buy OTM Call + OTM Put)
   ═══════════════════════════════════════════
   • Cheaper than straddle
   • Needs even BIGGER move to profit
   • Both options can expire worthless
   
   Risk: Same as straddle but needs more movement

3. SELL PREMIUM (Advanced - High Risk)
   ═══════════════════════════════════════════
   • Sell options BEFORE earnings (collect high premium)
   • Profit from IV crush AFTER earnings
   • Need the stock to NOT move much
   
   Risk: UNLIMITED if wrong (naked calls)
   Use spreads to limit risk!

4. BUY POST-EARNINGS (Safer for beginners)
   ═══════════════════════════════════════════
   • WAIT until after earnings
   • IV drops = cheaper options
   • Make directional bet with lower premium
   
   Risk: Lower, but need strong conviction

5. CALENDAR SPREAD
   ═══════════════════════════════════════════
   • Sell near-term option (before earnings)
   • Buy far-term option (after earnings)
   • Profit from IV crush on near-term
   
   Risk: Medium complexity

═══════════════════════════════════════════════════════════════

THE BRUTAL TRUTH ABOUT EARNINGS:

"Buy the rumor, sell the news" applies to options too!

Before Earnings:
  ✗ Options are EXPENSIVE (IV pumped up)
  ✗ Everyone expects big move
  ✗ Premium is "priced in"

After Earnings:
  ✓ IV collapses ("IV Crush")
  ✓ Even if stock moved your way, option can lose value
  ✓ Time decay + IV crush = double hit

Example:
  Before: Stock $100, ATM call costs $5 (high IV)
  After: Stock moves to $105 (you were right!)
  But: Option now worth $4 (IV crushed)
  Result: You LOST money despite being right!

═══════════════════════════════════════════════════════════════

SAFER APPROACHES:
1. Wait until AFTER earnings, then trade
2. Use stock instead of options for earnings
3. Use small position sizes (1% of portfolio max)
4. Paper trade earnings first to learn
5. Avoid weeklies - use monthlies
""")


# ============================================================================
# QUICK REFERENCE GUIDE
# ============================================================================

def quick_reference():
    """
    Quick reference guide for common options concepts.
    """
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                     OPTIONS TRADING QUICK REFERENCE                        ║
╚════════════════════════════════════════════════════════════════════════════╝

BASIC POSITIONS:
═══════════════════════════════════════════════════════════════════════════
Long Call       │ Bullish      │ Max Loss: Premium  │ Max Gain: Unlimited
Long Put        │ Bearish      │ Max Loss: Premium  │ Max Gain: Strike - Premium
Short Call      │ Bearish      │ Max Loss: Unlimited│ Max Gain: Premium
Short Put       │ Bullish      │ Max Loss: Strike   │ Max Gain: Premium
Covered Call    │ Neutral/Bull │ Limited upside     │ Income generation
Protective Put  │ Insurance    │ Limited downside   │ Keeps upside

THE GREEKS:
═══════════════════════════════════════════════════════════════════════════
Delta (Δ)   │ 0 to 1.00 (calls) │ Directional sensitivity
            │ -1 to 0 (puts)    │ Also: % chance of ITM
            │
Gamma (Γ)   │ Highest ATM       │ How fast Delta changes
            │ Low ITM/OTM       │ Risk amplifier
            │
Theta (Θ)   │ Negative value    │ Time decay per day
            │ Accelerates near  │ Seller's friend
            │ expiration        │ Buyer's enemy
            │
Vega (ν)    │ Positive value    │ Volatility sensitivity
            │ Highest ATM       │ Earnings = high vega

MONEYNESS:
═══════════════════════════════════════════════════════════════════════════
ITM (In The Money)     │ Calls: Strike < Stock  │ Has intrinsic value
ATM (At The Money)     │ Strike ≈ Stock price   │ Most liquid
OTM (Out of The Money) │ Calls: Strike > Stock  │ Only time value

COMMON STRATEGIES:
═══════════════════════════════════════════════════════════════════════════
Covered Call      │ Own stock + Sell call    │ Income in flat/up market
Cash-Secured Put  │ Sell put + Keep cash     │ Get paid to buy stock
Protective Put    │ Own stock + Buy put      │ Downside protection
Collar            │ Covered call + Prot put  │ Limited risk/reward
Vertical Spread   │ Buy + Sell same type     │ Defined risk/reward
Iron Condor       │ Sell OTM put + call      │ Neutral strategy
Straddle          │ Buy call + put same K    │ Big move expected
Strangle          │ Buy OTM call + put       │ Bigger move needed

RULES OF THUMB:
═══════════════════════════════════════════════════════════════════════════
✓ Buy options 30+ days out (more time = less decay)
✓ Sell options 30-45 days out (sweet spot for theta)
✓ Risk 1-2% per trade maximum
✓ Take profits at 50-100%
✓ Cut losses at 50%
✓ Never trade options during first/last 30 min of day
✓ Check liquidity: bid/ask spread should be < 10% of price
✓ Avoid holding through earnings unless specifically trading it
✓ Paper trade for 1-3 months before using real money

RED FLAGS:
═══════════════════════════════════════════════════════════════════════════
✗ Wide bid/ask spreads (illiquid)
✗ Very cheap options (usually for a reason)
✗ Very expensive options (IV too high)
✗ Trading weekly options as beginner
✗ Selling naked options (unlimited risk)
✗ Not knowing your max loss before entering
✗ Hoping a losing trade will recover
✗ Revenge trading after losses

MARKET HOURS & EXPIRATION:
═══════════════════════════════════════════════════════════════════════════
Market Hours     │ 9:30 AM - 4:00 PM ET
Options Expire   │ 3rd Friday of month (monthly)
                 │ Various days (weekly)
Settlement       │ Next business day after expiration
Last Trade Day   │ Expiration day (until 4:00 PM ET)

RESOURCES:
═══════════════════════════════════════════════════════════════════════════
• Alpaca API: docs.alpaca.markets
• Options Calculator: optionsprofitcalculator.com
• Learn: tastytrade.com, optionalpha.com
• Greeks calculator: Most broker platforms
• IV data: marketchameleon.com

Remember: This is a GUIDE, not financial advice.
Always do your own research and never risk more than you can afford to lose!
""")


# ============================================================================
# MAIN MENU
# ============================================================================

def main_menu():
    """Main menu for the options scanner."""
    
    # Popular liquid stocks for scanning
    WATCHLIST = [
        'SPY', 'QQQ', 'IWM',  # ETFs
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META',  # Big Tech
        'TSLA', 'NVDA', 'AMD', 'INTC',  # Tech/Semi
        'JPM', 'BAC', 'WFC', 'GS',  # Finance
        'XOM', 'CVX', 'COP',  # Energy
        'DIS', 'NFLX', 'BA', 'NKE'  # Consumer
    ]
    
    while True:
        print("\n" + "="*80)
        print(" "*25 + "OPTIONS SCANNER & ANALYZER")
        print("="*80)
        print("""
1. Scan for High IV Opportunities (SELLING premium)
2. Scan for Low IV Opportunities (BUYING options)
3. Analyze Specific Stock's Options Chain
4. Earnings Play Analyzer
5. Quick Reference Guide
6. Custom Watchlist Scanner
0. Exit

Note: Scanning ~25 stocks, may take a minute...
""")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            scan_high_iv_opportunities(WATCHLIST)
        
        elif choice == '2':
            scan_low_iv_opportunities(WATCHLIST)
        
        elif choice == '3':
            symbol = input("Enter stock symbol (e.g., AAPL): ").upper()
            days = input("Days to expiration (default 30): ")
            days = int(days) if days.isdigit() else 30
            analyze_options_chain(symbol, days)
        
        elif choice == '4':
            symbol = input("Enter stock symbol (e.g., AAPL): ").upper()
            earnings_play_analyzer(symbol)
        
        elif choice == '5':
            quick_reference()
        
        elif choice == '6':
            symbols = input("Enter symbols separated by spaces (e.g., AAPL TSLA MSFT): ")
            symbol_list = symbols.upper().split()
            
            scan_type = input("Scan for (1) High IV or (2) Low IV? ")
            if scan_type == '1':
                scan_high_iv_opportunities(symbol_list)
            else:
                scan_low_iv_opportunities(symbol_list)
        
        elif choice == '0':
            print("\nHappy trading! Remember: Practice with paper trading first!")
            break
        
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main_menu()