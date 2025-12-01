"""
Options Trading Learning Guide with Alpaca API
===============================================

This guide assumes you have:
- Alpaca account with options trading enabled
- API keys set in environment variables (APCA_API_KEY_ID, APCA_API_SECRET_KEY)
- Paper trading enabled for learning

Options Basics:
--------------
- CALL: Right (not obligation) to BUY stock at strike price before expiration
- PUT: Right (not obligation) to SELL stock at strike price before expiration
- Premium: Price you pay to buy the option
- Strike Price: The price at which you can buy/sell the underlying
- Expiration: Date when option expires
- ITM (In The Money): Call strike < stock price, Put strike > stock price
- OTM (Out of The Money): Call strike > stock price, Put strike < stock price
- ATM (At The Money): Strike price ≈ stock price
"""

import os
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOptionContractsRequest
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest
from datetime import datetime, timedelta
import pandas as pd

# Initialize clients
trading_client = TradingClient(
    api_key=os.getenv('APCA_API_KEY_ID'),
    secret_key=os.getenv('APCA_API_SECRET_KEY'),
    paper=True  # Always use paper trading for learning!
)

data_client = StockHistoricalDataClient(
    api_key=os.getenv('APCA_API_KEY_ID'),
    secret_key=os.getenv('APCA_API_SECRET_KEY')
)


# ============================================================================
# LESSON 1: Understanding the Options Chain
# ============================================================================

def lesson_1_get_options_chain(symbol='SPY', days_to_expiry=30):
    """
    Fetch and understand the options chain.
    
    An options chain shows all available options for a stock:
    - Multiple expiration dates
    - Multiple strike prices for each expiration
    - Both calls and puts
    """
    print(f"\n{'='*80}")
    print(f"LESSON 1: Exploring Options Chain for {symbol}")
    print(f"{'='*80}\n")
    
    # First, get the current stock price
    quote_request = StockLatestQuoteRequest(symbol_or_symbols=symbol)
    quote = data_client.get_stock_latest_quote(quote_request)[symbol]
    current_price = (quote.ask_price + quote.bid_price) / 2
    
    print(f"Current {symbol} price: ${current_price:.2f}\n")
    
    # Get options expiring within the next X days
    expiry_date = (datetime.now() + timedelta(days=days_to_expiry)).strftime('%Y-%m-%d')
    
    request = GetOptionContractsRequest(
        underlying_symbols=[symbol],
        expiration_date_gte=datetime.now().strftime('%Y-%m-%d'),
        expiration_date_lte=expiry_date,
        limit=100
    )
    
    options = trading_client.get_option_contracts(request)
    
    if not options.option_contracts:
        print("No options found. Check if options trading is enabled for your account.")
        return None
    
    # Organize by expiration date
    by_expiry = {}
    for opt in options.option_contracts:
        exp = opt.expiration_date
        if exp not in by_expiry:
            by_expiry[exp] = {'calls': [], 'puts': []}
        
        if opt.type == 'call':
            by_expiry[exp]['calls'].append(opt)
        else:
            by_expiry[exp]['puts'].append(opt)
    
    # Show the first expiration date as an example
    first_expiry = sorted(by_expiry.keys())[0]
    print(f"Options expiring on: {first_expiry}")
    print(f"Days until expiration: {(first_expiry - datetime.now().date()).days}")
    print("\n" + "-"*80)
    
    # Show calls and puts side by side
    calls = sorted(by_expiry[first_expiry]['calls'], key=lambda x: x.strike_price)
    puts = sorted(by_expiry[first_expiry]['puts'], key=lambda x: x.strike_price)
    
    print(f"\n{'CALLS':^40} | {'PUTS':^40}")
    print(f"{'Strike':<10} {'Symbol':<28} | {'Strike':<10} {'Symbol':<28}")
    print("-"*80)
    
    for call, put in zip(calls[:10], puts[:10]):  # Show first 10
        call_mark = "*" if abs(call.strike_price - current_price) < 5 else " "
        put_mark = "*" if abs(put.strike_price - current_price) < 5 else " "
        print(f"{call_mark}${call.strike_price:<8.2f} {call.symbol:<28} | "
              f"{put_mark}${put.strike_price:<8.2f} {put.symbol:<28}")
    
    print("\n* = Near current price (ATM - At The Money)")
    print("\nKey Insight: Options near the current price (ATM) are most actively traded")
    
    return by_expiry


# ============================================================================
# LESSON 2: Understanding Call Options
# ============================================================================

def lesson_2_analyze_call_option(symbol='SPY'):
    """
    Deep dive into call options.
    
    CALL OPTION = Betting the stock will go UP
    - You pay a premium
    - If stock goes above strike + premium, you profit
    - If stock stays below strike, you lose the premium (max loss)
    """
    print(f"\n{'='*80}")
    print(f"LESSON 2: Understanding Call Options")
    print(f"{'='*80}\n")
    
    # Get current price
    quote = data_client.get_stock_latest_quote(
        StockLatestQuoteRequest(symbol_or_symbols=symbol)
    )[symbol]
    current_price = (quote.ask_price + quote.bid_price) / 2
    
    print(f"Current {symbol} price: ${current_price:.2f}\n")
    
    # Get ATM call option (strike near current price)
    expiry_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    
    request = GetOptionContractsRequest(
        underlying_symbols=[symbol],
        expiration_date_gte=datetime.now().strftime('%Y-%m-%d'),
        expiration_date_lte=expiry_date,
        type='call',
        limit=50
    )
    
    calls = trading_client.get_option_contracts(request).option_contracts
    
    # Find the call closest to current price (ATM)
    atm_call = min(calls, key=lambda x: abs(x.strike_price - current_price))
    
    print(f"Example ATM Call Option:")
    print(f"Symbol: {atm_call.symbol}")
    print(f"Strike Price: ${atm_call.strike_price:.2f}")
    print(f"Expiration: {atm_call.expiration_date}")
    print(f"Days to expiry: {(atm_call.expiration_date - datetime.now().date()).days}")
    
    # Let's simulate scenarios
    print("\n" + "-"*80)
    print("PROFIT/LOSS SCENARIOS (assuming premium of $3.00 per share)")
    print("-"*80)
    
    premium = 3.00  # Example premium
    strike = atm_call.strike_price
    
    scenarios = [
        ("Stock drops to", current_price - 10),
        ("Stock stays same", current_price),
        ("Stock up slightly", strike + premium / 2),
        ("Stock at breakeven", strike + premium),
        ("Stock up nicely", strike + premium + 5),
        ("Stock up big", strike + premium + 10),
    ]
    
    print(f"\n{'Scenario':<25} {'Stock Price':<15} {'Option Value':<15} {'P/L per share':<15} {'P/L %'}")
    print("-"*80)
    
    for scenario, stock_price in scenarios:
        # Option value at expiration = max(stock_price - strike, 0)
        option_value = max(stock_price - strike, 0)
        profit_loss = option_value - premium
        pl_pct = (profit_loss / premium) * 100
        
        print(f"{scenario:<25} ${stock_price:<14.2f} ${option_value:<14.2f} "
              f"${profit_loss:<14.2f} {pl_pct:>6.1f}%")
    
    print("\n" + "="*80)
    print("KEY INSIGHTS:")
    print("="*80)
    print(f"1. Breakeven = Strike + Premium = ${strike:.2f} + ${premium:.2f} = ${strike + premium:.2f}")
    print(f"2. Max Loss = Premium paid = ${premium:.2f} (if stock <= strike)")
    print(f"3. Max Gain = Unlimited (as stock goes up)")
    print(f"4. You need stock to move UP more than the premium to profit")
    
    return atm_call


# ============================================================================
# LESSON 3: Understanding Put Options
# ============================================================================

def lesson_3_analyze_put_option(symbol='SPY'):
    """
    Deep dive into put options.
    
    PUT OPTION = Betting the stock will go DOWN (or protection against drops)
    - You pay a premium
    - If stock goes below strike - premium, you profit
    - If stock stays above strike, you lose the premium (max loss)
    """
    print(f"\n{'='*80}")
    print(f"LESSON 3: Understanding Put Options")
    print(f"{'='*80}\n")
    
    # Get current price
    quote = data_client.get_stock_latest_quote(
        StockLatestQuoteRequest(symbol_or_symbols=symbol)
    )[symbol]
    current_price = (quote.ask_price + quote.bid_price) / 2
    
    print(f"Current {symbol} price: ${current_price:.2f}\n")
    
    # Get ATM put option
    expiry_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    
    request = GetOptionContractsRequest(
        underlying_symbols=[symbol],
        expiration_date_gte=datetime.now().strftime('%Y-%m-%d'),
        expiration_date_lte=expiry_date,
        type='put',
        limit=50
    )
    
    puts = trading_client.get_option_contracts(request).option_contracts
    atm_put = min(puts, key=lambda x: abs(x.strike_price - current_price))
    
    print(f"Example ATM Put Option:")
    print(f"Symbol: {atm_put.symbol}")
    print(f"Strike Price: ${atm_put.strike_price:.2f}")
    print(f"Expiration: {atm_put.expiration_date}")
    
    # Simulate scenarios
    print("\n" + "-"*80)
    print("PROFIT/LOSS SCENARIOS (assuming premium of $3.00 per share)")
    print("-"*80)
    
    premium = 3.00
    strike = atm_put.strike_price
    
    scenarios = [
        ("Stock up big", current_price + 10),
        ("Stock up slightly", current_price + 5),
        ("Stock stays same", current_price),
        ("Stock at breakeven", strike - premium),
        ("Stock down nicely", strike - premium - 5),
        ("Stock down big", strike - premium - 10),
    ]
    
    print(f"\n{'Scenario':<25} {'Stock Price':<15} {'Option Value':<15} {'P/L per share':<15} {'P/L %'}")
    print("-"*80)
    
    for scenario, stock_price in scenarios:
        # Put value = max(strike - stock_price, 0)
        option_value = max(strike - stock_price, 0)
        profit_loss = option_value - premium
        pl_pct = (profit_loss / premium) * 100
        
        print(f"{scenario:<25} ${stock_price:<14.2f} ${option_value:<14.2f} "
              f"${profit_loss:<14.2f} {pl_pct:>6.1f}%")
    
    print("\n" + "="*80)
    print("KEY INSIGHTS:")
    print("="*80)
    print(f"1. Breakeven = Strike - Premium = ${strike:.2f} - ${premium:.2f} = ${strike - premium:.2f}")
    print(f"2. Max Loss = Premium paid = ${premium:.2f} (if stock >= strike)")
    print(f"3. Max Gain = Strike - Premium (if stock goes to $0)")
    print(f"4. You need stock to move DOWN more than the premium to profit")
    
    return atm_put


# ============================================================================
# LESSON 4: ITM vs ATM vs OTM
# ============================================================================

def lesson_4_moneyness_comparison(symbol='SPY'):
    """
    Understanding In-The-Money, At-The-Money, and Out-of-The-Money options.
    
    This is CRUCIAL for options trading!
    """
    print(f"\n{'='*80}")
    print(f"LESSON 4: ITM vs ATM vs OTM Options")
    print(f"{'='*80}\n")
    
    quote = data_client.get_stock_latest_quote(
        StockLatestQuoteRequest(symbol_or_symbols=symbol)
    )[symbol]
    current_price = (quote.ask_price + quote.bid_price) / 2
    
    print(f"Current {symbol} price: ${current_price:.2f}\n")
    
    expiry_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    
    # Get calls
    request = GetOptionContractsRequest(
        underlying_symbols=[symbol],
        expiration_date_gte=datetime.now().strftime('%Y-%m-%d'),
        expiration_date_lte=expiry_date,
        type='call',
        limit=100
    )
    
    calls = sorted(
        trading_client.get_option_contracts(request).option_contracts,
        key=lambda x: x.strike_price
    )
    
    # Find examples of each type
    itm_call = next((c for c in calls if c.strike_price < current_price - 5), None)
    atm_call = min(calls, key=lambda x: abs(x.strike_price - current_price))
    otm_call = next((c for c in calls if c.strike_price > current_price + 5), None)
    
    print("CALL OPTIONS:")
    print("-" * 80)
    print(f"\n{'Type':<15} {'Strike':<12} {'Moneyness':<30} {'Typical Premium'}")
    print("-" * 80)
    
    if itm_call:
        intrinsic = current_price - itm_call.strike_price
        print(f"ITM (In)       ${itm_call.strike_price:<10.2f}  Below current price           "
              f"HIGH (has ${intrinsic:.2f} intrinsic value)")
    
    print(f"ATM (At)       ${atm_call.strike_price:<10.2f}  Near current price            "
          f"MEDIUM (mostly time value)")
    
    if otm_call:
        print(f"OTM (Out)      ${otm_call.strike_price:<10.2f}  Above current price           "
              f"LOW (only time value)")
    
    print("\n" + "="*80)
    print("UNDERSTANDING THE TRADE-OFFS:")
    print("="*80)
    print("""
ITM (In-The-Money) Options:
  ✓ Already profitable
  ✓ More expensive (higher premium)
  ✓ Less risk, but less leverage
  ✓ Better for conservative plays
  Example: If SPY is $450, a $440 call is ITM
  
ATM (At-The-Money) Options:
  ✓ Strike ≈ current price
  ✓ Medium premium
  ✓ Good balance of risk/reward
  ✓ Most actively traded
  Example: If SPY is $450, a $450 call is ATM
  
OTM (Out-of-The-Money) Options:
  ✓ Not yet profitable
  ✓ Cheapest (lowest premium)
  ✓ High risk, high reward (lottery ticket)
  ✓ Can expire worthless
  Example: If SPY is $450, a $460 call is OTM
""")
    
    return {'itm': itm_call, 'atm': atm_call, 'otm': otm_call}


# ============================================================================
# LESSON 5: Time Decay (Theta)
# ============================================================================

def lesson_5_time_decay(symbol='SPY'):
    """
    Understanding time decay - how options lose value as expiration approaches.
    
    This is one of the most important concepts in options!
    """
    print(f"\n{'='*80}")
    print(f"LESSON 5: Time Decay (Theta) - The Silent Killer")
    print(f"{'='*80}\n")
    
    quote = data_client.get_stock_latest_quote(
        StockLatestQuoteRequest(symbol_or_symbols=symbol)
    )[symbol]
    current_price = (quote.ask_price + quote.bid_price) / 2
    
    print(f"Current {symbol} price: ${current_price:.2f}\n")
    
    # Get options at different expirations
    expirations = [7, 30, 60, 90]
    atm_options = []
    
    for days in expirations:
        expiry_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        
        request = GetOptionContractsRequest(
            underlying_symbols=[symbol],
            expiration_date_gte=expiry_date,
            expiration_date_lte=expiry_date,
            type='call',
            limit=50
        )
        
        calls = trading_client.get_option_contracts(request).option_contracts
        if calls:
            atm = min(calls, key=lambda x: abs(x.strike_price - current_price))
            atm_options.append((days, atm))
    
    print("ATM CALL OPTIONS AT DIFFERENT EXPIRATIONS:")
    print("-" * 80)
    print(f"{'Days to Expiry':<20} {'Strike':<15} {'Symbol'}")
    print("-" * 80)
    
    for days, opt in atm_options:
        print(f"{days:<20} ${opt.strike_price:<14.2f} {opt.symbol}")
    
    print("\n" + "="*80)
    print("TIME DECAY INSIGHTS:")
    print("="*80)
    print("""
1. TIME DECAY ACCELERATES as expiration approaches
   - Slow decay when >30 days out
   - Rapid decay in the last 2 weeks
   - Fastest in the last 3 days
   
2. ATM options decay fastest
   - They have the most time value to lose
   - ITM/OTM decay slower
   
3. Weekend effect: Time passes but stock doesn't trade
   - You lose time value over weekends
   - Friday options are risky!
   
4. For BUYERS: Time decay works AGAINST you
   - You need the stock to move enough to overcome decay
   - Longer-dated options give you more time
   
5. For SELLERS: Time decay works FOR you
   - You profit as the option loses value
   - Selling options = collecting time premium
   
PRACTICAL ADVICE:
- Buying options? Give yourself enough time (30+ days)
- Don't buy options expiring in < 7 days unless very confident
- Consider selling options to benefit from time decay
""")


# ============================================================================
# MAIN LEARNING PROGRAM
# ============================================================================

def run_all_lessons():
    """
    Run through all lessons in sequence.
    """
    symbol = 'SPY'  # S&P 500 ETF - most liquid options market
    
    print("\n" + "="*80)
    print(" "*20 + "OPTIONS TRADING LEARNING PROGRAM")
    print(" "*25 + f"Using {symbol} as example")
    print("="*80)
    
    try:
        # Lesson 1: Options Chain
        lesson_1_get_options_chain(symbol)
        input("\nPress Enter to continue to Lesson 2...")
        
        # Lesson 2: Call Options
        lesson_2_analyze_call_option(symbol)
        input("\nPress Enter to continue to Lesson 3...")
        
        # Lesson 3: Put Options
        lesson_3_analyze_put_option(symbol)
        input("\nPress Enter to continue to Lesson 4...")
        
        # Lesson 4: Moneyness
        lesson_4_moneyness_comparison(symbol)
        input("\nPress Enter to continue to Lesson 5...")
        
        # Lesson 5: Time Decay
        lesson_5_time_decay(symbol)
        
        print("\n" + "="*80)
        print("CONGRATULATIONS! You've completed the basics.")
        print("="*80)
        print("""
Next steps:
1. Study the Greeks (Delta, Gamma, Theta, Vega)
2. Learn basic strategies (covered calls, protective puts)
3. Practice with paper trading
4. NEVER risk more than you can afford to lose!
""")
        
    except Exception as e:
        print(f"\nError occurred: {e}")
        print("\nMake sure:")
        print("1. Your Alpaca account has options trading enabled")
        print("2. Your API keys are set correctly")
        print("3. You're using paper trading for learning")


if __name__ == "__main__":
    # Set your API keys as environment variables before running:
    # export APCA_API_KEY_ID="your_key"
    # export APCA_API_SECRET_KEY="your_secret"
    
    run_all_lessons()