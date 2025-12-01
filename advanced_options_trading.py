"""
Advanced Options Trading Examples with Alpaca
==============================================

This file covers:
1. Understanding the Greeks
2. Basic options strategies
3. Risk management
4. Actual trading examples (paper trading)
"""

import os
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import (
    GetOptionContractsRequest,
    MarketOrderRequest,
    LimitOrderRequest
)
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus
from alpaca.data.historical import StockHistoricalDataClient, OptionHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest
from datetime import datetime, timedelta
import pandas as pd

# Initialize clients
trading_client = TradingClient(
    api_key=os.getenv('APCA_API_KEY_ID'),
    secret_key=os.getenv('APCA_API_SECRET_KEY'),
    paper=True  # ALWAYS use paper trading for learning!
)

stock_data_client = StockHistoricalDataClient(
    api_key=os.getenv('APCA_API_KEY_ID'),
    secret_key=os.getenv('APCA_API_SECRET_KEY')
)


# ============================================================================
# ADVANCED 1: Understanding the Greeks
# ============================================================================

def advanced_1_greeks_explained(symbol='SPY'):
    """
    The Greeks measure how options prices change with various factors.
    
    - Delta: How much option price changes per $1 stock move
    - Gamma: How much delta changes per $1 stock move
    - Theta: How much option loses per day (time decay)
    - Vega: How much option price changes per 1% change in volatility
    """
    print(f"\n{'='*80}")
    print(f"ADVANCED 1: Understanding the Greeks")
    print(f"{'='*80}\n")
    
    quote = stock_data_client.get_stock_latest_quote(
        StockLatestQuoteRequest(symbol_or_symbols=symbol)
    )[symbol]
    current_price = (quote.ask_price + quote.bid_price) / 2
    
    print(f"Current {symbol} price: ${current_price:.2f}\n")
    
    # Get some options
    expiry_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    
    request = GetOptionContractsRequest(
        underlying_symbols=[symbol],
        expiration_date_gte=datetime.now().strftime('%Y-%m-%d'),
        expiration_date_lte=expiry_date,
        type='call',
        limit=50
    )
    
    calls = sorted(
        trading_client.get_option_contracts(request).option_contracts,
        key=lambda x: x.strike_price
    )
    
    print("THE GREEKS EXPLAINED WITH EXAMPLES:")
    print("="*80)
    
    print("\n1. DELTA (Δ): Directional Risk")
    print("-" * 80)
    print("""
Delta measures how much the option price changes for a $1 move in the stock.

Call Options:
  • ITM calls: Delta ≈ 0.70 to 1.00 (moves almost like stock)
  • ATM calls: Delta ≈ 0.50 (moves half as much as stock)
  • OTM calls: Delta ≈ 0.10 to 0.40 (smaller moves)

Put Options:
  • ITM puts: Delta ≈ -0.70 to -1.00 (negative = inverse to stock)
  • ATM puts: Delta ≈ -0.50
  • OTM puts: Delta ≈ -0.40 to -0.10

Example: If you own a call with Delta = 0.50:
  • Stock goes up $1 → Option gains ~$0.50
  • Stock goes up $10 → Option gains ~$5.00
  
PRO TIP: Delta also approximates probability of expiring ITM
  • Delta 0.50 = ~50% chance of profit
  • Delta 0.30 = ~30% chance of profit
""")
    
    print("\n2. GAMMA (Γ): Delta Risk")
    print("-" * 80)
    print("""
Gamma measures how much Delta changes as the stock price moves.

High Gamma (ATM options):
  • Delta changes rapidly
  • More "exciting" - bigger swings
  • Can work for or against you fast
  
Low Gamma (ITM/OTM options):
  • Delta changes slowly
  • More stable behavior
  • Less responsive to price moves

Example: Call with Delta 0.50, Gamma 0.05:
  • Stock up $1 → New Delta becomes 0.55
  • Stock up $2 → New Delta becomes 0.60
  • And so on...

WARNING: Near expiration, ATM options have EXTREME gamma
  • Small stock moves = huge option swings
  • Very risky for buyers and sellers!
""")
    
    print("\n3. THETA (Θ): Time Decay")
    print("-" * 80)
    print("""
Theta measures how much value the option loses per day.

Typical Theta values:
  • 30 days out: -$0.10/day for ATM option
  • 7 days out: -$0.30/day for ATM option
  • 1 day out: -$0.50+/day for ATM option

Example: Option worth $3.00 with Theta = -0.15:
  • Tomorrow (all else equal): Worth $2.85
  • In 5 days: Worth $2.25
  • In 10 days: Worth $1.50

CRITICAL INSIGHT:
  • Time decay ACCELERATES near expiration
  • Weekends still decay! (but stock doesn't move)
  • ATM options have highest theta
  
For buyers: Theta is your enemy
For sellers: Theta is your friend
""")
    
    print("\n4. VEGA (ν): Volatility Risk")
    print("-" * 80)
    print("""
Vega measures how much option price changes per 1% change in implied volatility.

High volatility = Higher option prices (for both calls and puts)
Low volatility = Lower option prices

Example: Option worth $3.00 with Vega = 0.20:
  • If volatility goes from 20% to 21%: Option → $3.20
  • If volatility goes from 20% to 19%: Option → $2.80

REAL-WORLD EXAMPLES:
  • Earnings announcements: Volatility spikes → Options expensive
  • After earnings: Volatility crashes → Options lose value fast ("IV crush")
  • Market calm: Low volatility → Options cheap
  • Market panic: High volatility → Options expensive

TRADING STRATEGY:
  • Buy options when volatility is low (before events)
  • Sell options when volatility is high (after events)
  • Be aware of earnings dates!
""")
    
    # Show some actual examples from the chain
    print("\n" + "="*80)
    print("REAL EXAMPLES FROM OPTIONS CHAIN:")
    print("="*80 + "\n")
    
    print(f"{'Type':<10} {'Strike':<12} {'Delta (approx)':<20} {'Behavior'}")
    print("-" * 80)
    
    # Find ITM, ATM, OTM examples
    for call in calls:
        if call.strike_price < current_price - 10:
            print(f"ITM Call   ${call.strike_price:<10.2f}  ~0.70-0.90          Moves like stock")
            break
    
    atm = min(calls, key=lambda x: abs(x.strike_price - current_price))
    print(f"ATM Call   ${atm.strike_price:<10.2f}  ~0.50              Balanced exposure")
    
    for call in calls:
        if call.strike_price > current_price + 10:
            print(f"OTM Call   ${call.strike_price:<10.2f}  ~0.20-0.30         Lottery ticket")
            break


# ============================================================================
# ADVANCED 2: Basic Options Strategies
# ============================================================================

def advanced_2_covered_call_strategy(symbol='AAPL'):
    """
    COVERED CALL: Most popular options strategy for beginners.
    
    Strategy:
    1. Own 100 shares of stock
    2. Sell 1 call option (collect premium)
    3. Keep premium if stock doesn't reach strike
    4. Sell stock at strike if it does
    
    Risk: Limited upside (capped at strike)
    Reward: Premium income + potential stock gains
    """
    print(f"\n{'='*80}")
    print(f"ADVANCED 2: Covered Call Strategy (Income Generation)")
    print(f"{'='*80}\n")
    
    quote = stock_data_client.get_stock_latest_quote(
        StockLatestQuoteRequest(symbol_or_symbols=symbol)
    )[symbol]
    current_price = (quote.ask_price + quote.bid_price) / 2
    
    print(f"Current {symbol} price: ${current_price:.2f}\n")
    
    # Get OTM calls (strikes above current price)
    expiry_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    
    request = GetOptionContractsRequest(
        underlying_symbols=[symbol],
        expiration_date_gte=datetime.now().strftime('%Y-%m-%d'),
        expiration_date_lte=expiry_date,
        type='call',
        limit=50
    )
    
    calls = [c for c in trading_client.get_option_contracts(request).option_contracts
             if c.strike_price > current_price]
    
    if not calls:
        print("No suitable calls found")
        return
    
    calls = sorted(calls, key=lambda x: x.strike_price)
    
    print("COVERED CALL STRATEGY EXPLANATION:")
    print("="*80)
    print(f"""
Step 1: Buy 100 shares of {symbol} at ${current_price:.2f}
        Cost: ${current_price * 100:.2f}

Step 2: Sell 1 call option (you choose strike above current price)
        
Let's look at some options:
""")
    
    print(f"\n{'Strike':<12} {'Distance':<15} {'Est. Premium':<15} {'Max Profit':<15} {'Annualized'}")
    print("-" * 80)
    
    for call in calls[:5]:
        distance = call.strike_price - current_price
        pct_otm = (distance / current_price) * 100
        
        # Estimate premium (rough approximation)
        est_premium = max(0.5, distance * 0.1) * 100  # Per contract
        
        # Calculate max profit
        stock_gain = distance * 100
        total_profit = stock_gain + est_premium
        
        # Annualize it (assuming 30 days)
        annualized_return = (total_profit / (current_price * 100)) * (365 / 30) * 100
        
        print(f"${call.strike_price:<10.2f} +${distance:.2f} ({pct_otm:>4.1f}%)   "
              f"~${est_premium:<13.2f} ${total_profit:<14.2f} {annualized_return:>6.1f}%")
    
    print("\n" + "="*80)
    print("SCENARIOS AT EXPIRATION:")
    print("="*80)
    
    # Pick the first OTM call as example
    example_call = calls[0]
    est_premium = max(0.5, (example_call.strike_price - current_price) * 0.1) * 100
    
    print(f"\nExample: Sell ${example_call.strike_price} call, collect ~${est_premium:.2f} premium")
    print("-" * 80)
    
    scenarios = [
        ("Stock drops to", current_price * 0.95, "Keep shares + premium, can sell another call"),
        ("Stock stays flat", current_price, "Keep shares + premium, can sell another call"),
        ("Stock at strike", example_call.strike_price, "Shares called away at strike, keep premium"),
        ("Stock above strike", example_call.strike_price * 1.05, "Shares called away at strike, keep premium (miss upside)"),
    ]
    
    print(f"\n{'Scenario':<30} {'Stock Price':<15} {'Outcome'}")
    print("-" * 80)
    
    for scenario, price, outcome in scenarios:
        print(f"{scenario:<30} ${price:<14.2f} {outcome}")
    
    print("\n" + "="*80)
    print("PROS AND CONS:")
    print("="*80)
    print("""
PROS:
  ✓ Generate income from stocks you own
  ✓ Reduces your cost basis
  ✓ Works well in sideways/slightly bullish markets
  ✓ Lower risk than just holding stock
  
CONS:
  ✗ Limited upside (capped at strike)
  ✗ Still lose money if stock drops significantly
  ✗ Shares may get called away
  
BEST FOR:
  • Stocks you don't mind selling
  • Generating steady income
  • Neutral to slightly bullish outlook
  • Reducing volatility in your portfolio
""")


def advanced_3_protective_put_strategy(symbol='AAPL'):
    """
    PROTECTIVE PUT: Insurance for your stock holdings.
    
    Strategy:
    1. Own 100 shares of stock
    2. Buy 1 put option (pay premium)
    3. Limits downside risk
    
    Like buying insurance for your house!
    """
    print(f"\n{'='*80}")
    print(f"ADVANCED 3: Protective Put Strategy (Portfolio Insurance)")
    print(f"{'='*80}\n")
    
    quote = stock_data_client.get_stock_latest_quote(
        StockLatestQuoteRequest(symbol_or_symbols=symbol)
    )[symbol]
    current_price = (quote.ask_price + quote.bid_price) / 2
    
    print(f"Current {symbol} price: ${current_price:.2f}\n")
    
    # Get puts below current price
    expiry_date = (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d')
    
    request = GetOptionContractsRequest(
        underlying_symbols=[symbol],
        expiration_date_gte=datetime.now().strftime('%Y-%m-%d'),
        expiration_date_lte=expiry_date,
        type='put',
        limit=50
    )
    
    puts = [p for p in trading_client.get_option_contracts(request).option_contracts
            if p.strike_price < current_price]
    
    if not puts:
        print("No suitable puts found")
        return
    
    puts = sorted(puts, key=lambda x: x.strike_price, reverse=True)
    
    print("PROTECTIVE PUT STRATEGY EXPLANATION:")
    print("="*80)
    print(f"""
You own: 100 shares of {symbol} at ${current_price:.2f}
Value: ${current_price * 100:.2f}

Problem: What if the stock crashes?

Solution: Buy a put option (insurance)
""")
    
    print(f"\n{'Strike':<12} {'Protection':<20} {'Est. Premium':<15} {'Max Loss'}")
    print("-" * 80)
    
    for put in puts[:5]:
        distance = current_price - put.strike_price
        pct_below = (distance / current_price) * 100
        
        # Estimate premium
        days_to_exp = (put.expiration_date - datetime.now().date()).days
        est_premium = max(1.0, distance * 0.15 + (days_to_exp / 365) * current_price * 0.02) * 100
        
        # Max loss = stock drop to strike + premium paid
        max_loss = distance * 100 + est_premium
        max_loss_pct = (max_loss / (current_price * 100)) * 100
        
        print(f"${put.strike_price:<10.2f} {pct_below:>5.1f}% below      "
              f"~${est_premium:<13.2f} ${max_loss:.2f} ({max_loss_pct:.1f}%)")
    
    print("\n" + "="*80)
    print("EXAMPLE SCENARIOS:")
    print("="*80)
    
    example_put = puts[2]  # 3rd one as example
    est_premium = max(1.0, (current_price - example_put.strike_price) * 0.15) * 100
    
    print(f"\nExample: Buy ${example_put.strike_price} put for ~${est_premium:.2f}")
    print("-" * 80)
    
    scenarios = [
        ("CRASH: Stock drops 30%", current_price * 0.70),
        ("DROP: Stock drops 15%", current_price * 0.85),
        ("At strike price", example_put.strike_price),
        ("Flat: No change", current_price),
        ("UP: Stock gains 10%", current_price * 1.10),
        ("MOON: Stock gains 30%", current_price * 1.30),
    ]
    
    print(f"\n{'Scenario':<30} {'Stock Price':<15} {'Stock P/L':<15} {'Put Value':<15} {'Net P/L'}")
    print("-" * 80)
    
    for scenario, price in scenarios:
        stock_pl = (price - current_price) * 100
        put_value = max(example_put.strike_price - price, 0) * 100
        net_pl = stock_pl + put_value - est_premium
        
        print(f"{scenario:<30} ${price:<14.2f} ${stock_pl:<14.2f} "
              f"${put_value:<14.2f} ${net_pl:.2f}")
    
    print("\n" + "="*80)
    print("KEY INSIGHTS:")
    print("="*80)
    print(f"""
With protective put:
  • Max Loss: ~${(current_price - example_put.strike_price) * 100 + est_premium:.2f}
  • Without put: Could lose ${current_price * 100:.2f} if stock goes to $0!
  
Insurance cost: ~${est_premium:.2f} for {(example_put.expiration_date - datetime.now().date()).days} days
Cost per day: ~${est_premium / (example_put.expiration_date - datetime.now().date()).days:.2f}

PROS:
  ✓ Limited downside risk
  ✓ Keep unlimited upside
  ✓ Sleep better at night
  ✓ Good before earnings/volatile periods
  
CONS:
  ✗ Costs money (insurance premium)
  ✗ Reduces gains by premium amount
  ✗ Expires - need to renew
  
BEST FOR:
  • Protecting gains in stocks that have run up
  • Holding through uncertain periods
  • Peace of mind during volatility
""")


# ============================================================================
# ADVANCED 4: Paper Trading Example
# ============================================================================

def advanced_4_paper_trade_example(symbol='SPY'):
    """
    Actual example of placing an options trade (paper trading).
    
    WARNING: This demonstrates the mechanics only.
    Always do your own research before trading!
    """
    print(f"\n{'='*80}")
    print(f"ADVANCED 4: Placing an Options Trade (PAPER TRADING)")
    print(f"{'='*80}\n")
    
    # Check account
    account = trading_client.get_account()
    print(f"Account Status: {account.status}")
    print(f"Buying Power: ${float(account.buying_power):,.2f}")
    print(f"Cash: ${float(account.cash):,.2f}\n")
    
    # Get current price
    quote = stock_data_client.get_stock_latest_quote(
        StockLatestQuoteRequest(symbol_or_symbols=symbol)
    )[symbol]
    current_price = (quote.ask_price + quote.bid_price) / 2
    
    print(f"Current {symbol} price: ${current_price:.2f}\n")
    
    # Find an ATM call option
    expiry_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    
    request = GetOptionContractsRequest(
        underlying_symbols=[symbol],
        expiration_date_gte=datetime.now().strftime('%Y-%m-%d'),
        expiration_date_lte=expiry_date,
        type='call',
        limit=50
    )
    
    calls = trading_client.get_option_contracts(request).option_contracts
    atm_call = min(calls, key=lambda x: abs(x.strike_price - current_price))
    
    print("TRADE SETUP:")
    print("-" * 80)
    print(f"Action: BUY TO OPEN")
    print(f"Option: {atm_call.symbol}")
    print(f"Strike: ${atm_call.strike_price:.2f}")
    print(f"Expiration: {atm_call.expiration_date}")
    print(f"Type: Call")
    print(f"Quantity: 1 contract (100 shares)")
    
    print("\nThis is a PAPER TRADE for demonstration.")
    print("In real trading, you would:")
    print("  1. Analyze the option carefully")
    print("  2. Check the bid/ask spread")
    print("  3. Calculate your risk/reward")
    print("  4. Set appropriate stop losses")
    
    proceed = input("\nProceed with paper trade? (yes/no): ")
    
    if proceed.lower() != 'yes':
        print("Trade cancelled. Good decision to be cautious!")
        return
    
    try:
        # Place market order for 1 contract
        order_data = MarketOrderRequest(
            symbol=atm_call.symbol,
            qty=1,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY
        )
        
        order = trading_client.submit_order(order_data)
        
        print("\n" + "="*80)
        print("ORDER SUBMITTED!")
        print("="*80)
        print(f"Order ID: {order.id}")
        print(f"Status: {order.status}")
        print(f"Symbol: {order.symbol}")
        print(f"Quantity: {order.qty}")
        print(f"Side: {order.side}")
        
        print("\nYou can monitor this trade in your Alpaca paper trading dashboard.")
        print("\nREMEMBER: This is paper money. Always practice before using real money!")
        
    except Exception as e:
        print(f"\nError placing order: {e}")
        print("\nCommon issues:")
        print("  - Options trading not enabled on account")
        print("  - Insufficient buying power")
        print("  - Market closed")
        print("  - Invalid option symbol")


def view_open_positions():
    """
    View all open positions and orders.
    """
    print(f"\n{'='*80}")
    print(f"YOUR CURRENT POSITIONS")
    print(f"{'='*80}\n")
    
    try:
        # Get all positions
        positions = trading_client.get_all_positions()
        
        if not positions:
            print("No open positions.")
        else:
            print(f"{'Symbol':<30} {'Qty':<10} {'Avg Entry':<15} {'Current':<15} {'P/L'}")
            print("-" * 80)
            
            for pos in positions:
                pl = float(pos.unrealized_pl)
                pl_pct = float(pos.unrealized_plpc) * 100
                
                print(f"{pos.symbol:<30} {pos.qty:<10} "
                      f"${float(pos.avg_entry_price):<14.2f} "
                      f"${float(pos.current_price):<14.2f} "
                      f"${pl:.2f} ({pl_pct:+.2f}%)")
        
        # Get open orders
        orders = trading_client.get_orders(filter=QueryOrderStatus.OPEN)
        
        if orders:
            print("\n" + "="*80)
            print("OPEN ORDERS:")
            print("="*80 + "\n")
            
            for order in orders:
                print(f"Order ID: {order.id}")
                print(f"Symbol: {order.symbol}")
                print(f"Side: {order.side}")
                print(f"Qty: {order.qty}")
                print(f"Status: {order.status}")
                print("-" * 80)
        
    except Exception as e:
        print(f"Error: {e}")


# ============================================================================
# RISK MANAGEMENT
# ============================================================================

def risk_management_guidelines():
    """
    Critical risk management principles for options trading.
    """
    print(f"\n{'='*80}")
    print(f"RISK MANAGEMENT - THE MOST IMPORTANT LESSON")
    print(f"{'='*80}\n")
    
    print("""
1. POSITION SIZING
   ═══════════════════════════════════════════════════════════
   • Never risk more than 1-2% of your portfolio on a single trade
   • Options can go to $0 - only use money you can afford to lose
   • Start small while learning
   
   Example: $10,000 portfolio
     Max risk per trade: $100-$200
     If buying $2 options: Max 50-100 contracts
     If buying $5 options: Max 20-40 contracts

2. TIME FRAME
   ═══════════════════════════════════════════════════════════
   • Give yourself enough time - minimum 30 days
   • Avoid weekly options unless you're experienced
   • Time decay accelerates in last 2 weeks
   • Don't buy options expiring during holidays/weekends

3. STOP LOSSES
   ═══════════════════════════════════════════════════════════
   • Set mental or hard stop losses
   • Common rule: Cut losses at 50% of premium paid
   • Don't hope a losing trade will recover
   • It's okay to take small losses
   
   Example: Buy option for $3.00
     Stop loss at $1.50 (50% loss)
     If it hits $1.50, close the trade

4. PROFIT TAKING
   ═══════════════════════════════════════════════════════════
   • Don't be greedy
   • Consider taking profits at 50-100% gain
   • Scale out: sell half at 50%, let rest run
   • A profit secured is better than a profit lost

5. DIVERSIFICATION
   ═══════════════════════════════════════════════════════════
   • Don't put all eggs in one basket
   • Spread trades across different:
     * Stocks/ETFs
     * Expiration dates
     * Strategies
   • Avoid overconcentration in one sector

6. UNDERSTAND WHAT YOU'RE TRADING
   ═══════════════════════════════════════════════════════════
   • Know the Greeks for your position
   • Understand max profit and max loss
   • Be aware of upcoming events (earnings, Fed meetings)
   • Check implied volatility - don't overpay
   
7. AVOID COMMON MISTAKES
   ═══════════════════════════════════════════════════════════
   ✗ Buying options right before earnings (IV crush)
   ✗ Selling naked options (unlimited risk)
   ✗ Trading illiquid options (wide spreads)
   ✗ Revenge trading after losses
   ✗ Overleveraging with options
   ✗ Not having a plan before entering

8. PAPER TRADING FIRST
   ═══════════════════════════════════════════════════════════
   • Practice for at least 1-3 months
   • Test your strategies
   • Learn from mistakes with fake money
   • Understand order types and execution
   
9. KEEP A TRADING JOURNAL
   ═══════════════════════════════════════════════════════════
   • Record every trade: entry, exit, reason
   • Track what works and what doesn't
   • Review weekly/monthly
   • Learn from patterns
   
10. KNOW WHEN TO STOP
    ═══════════════════════════════════════════════════════════
    • Set daily/weekly loss limits
    • Don't trade when emotional
    • Take breaks after losses
    • Your mental health > profits
    
═══════════════════════════════════════════════════════════════

REMEMBER: 
  "The #1 rule is don't lose money.
   The #2 rule is don't forget rule #1."
   
Options can amplify both gains AND losses.
Treat them with respect, practice risk management,
and never trade with money you can't afford to lose.
""")


# ============================================================================
# MAIN PROGRAM
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print(" "*15 + "ADVANCED OPTIONS TRADING WITH ALPACA")
    print("="*80)
    print("""
Choose a lesson:

1. Understanding the Greeks (Delta, Gamma, Theta, Vega)
2. Covered Call Strategy (Generate Income)
3. Protective Put Strategy (Portfolio Insurance)
4. Paper Trading Example (Place actual trade)
5. View Your Open Positions
6. Risk Management Guidelines
7. Run All Advanced Lessons
0. Exit
""")
    
    choice = input("Enter your choice (0-7): ")
    
    if choice == '1':
        advanced_1_greeks_explained()
    elif choice == '2':
        advanced_2_covered_call_strategy()
    elif choice == '3':
        advanced_3_protective_put_strategy()
    elif choice == '4':
        advanced_4_paper_trade_example()
    elif choice == '5':
        view_open_positions()
    elif choice == '6':
        risk_management_guidelines()
    elif choice == '7':
        advanced_1_greeks_explained()
        input("\nPress Enter for next lesson...")
        advanced_2_covered_call_strategy()
        input("\nPress Enter for next lesson...")
        advanced_3_protective_put_strategy()
        input("\nPress Enter for next lesson...")
        risk_management_guidelines()
    elif choice == '0':
        print("Happy learning! Remember: paper trade first!")
    else:
        print("Invalid choice.")