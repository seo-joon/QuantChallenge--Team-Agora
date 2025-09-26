"""
Quant Challenge 2025

Algorithmic strategy template
"""

from enum import Enum
from typing import Optional
import numpy as np

class Side(Enum):
    BUY = 0
    SELL = 1

class Ticker(Enum):
    # TEAM_A (home team)
    TEAM_A = 0

def place_market_order(side: Side, ticker: Ticker, quantity: float) -> None:
    """Place a market order.
    
    Parameters
    ----------
    side
        Side of order to place
    ticker
        Ticker of order to place
    quantity
        Quantity of order to place
    """
    return

def place_limit_order(side: Side, ticker: Ticker, quantity: float, price: float, ioc: bool = False) -> int:
    """Place a limit order.
    
    Parameters
    ----------
    side
        Side of order to place
    ticker
        Ticker of order to place
    quantity
        Quantity of order to place
    price
        Price of order to place
    ioc
        Immediate or cancel flag (FOK)

    Returns
    -------
    order_id
        Order ID of order placed
    """
    return 0

def cancel_order(ticker: Ticker, order_id: int) -> bool:
    """Cancel an order.
    
    Parameters
    ----------
    ticker
        Ticker of order to cancel
    order_id
        Order ID of order to cancel

    Returns
    -------
    success
        True if order was cancelled, False otherwise
    """
    return 0

class Strategy:
    """Template for a strategy."""

    def reset_state(self) -> None:
        """Reset the state of the strategy to the start of game position.
        
        Since the sandbox execution can start mid-game, we recommend creating a
        function which can be called from __init__ and on_game_event_update (END_GAME).

        Note: In production execution, the game will start from the beginning
        and will not be replayed.
        """
        # info
        self.home_score = 0
        self.away_score = 0
        self.time_start = 2400
        self.time_left = 2400
        self.ticker = False
        self.last_traded_price = 50
        self.best_bid = 0
        self.best_ask = 100

        # my orders
        self.my_bid_id = False
        self.my_ask_id = False
        self.edge = 1
        self.delta = 0
        self.damp = 100
        self.cumTrades = 0        
        self.prior = 1

    def fair(self):
        logit = np.tan(
            np.pi/2 * 
            (self.home_score-self.away_score)/
            (self.home_score+self.away_score+self.prior))
        time_frac = self.time_left/self.time_start
        prob = 1/(1+np.exp(self.delta/self.damp-logit/time_frac))
        return 100 * prob

    def __init__(self) -> None:
        """Your initialization code goes here."""
        self.reset_state()

    def on_trade_update(
        self, ticker: Ticker, side: Side, quantity: float, price: float
    ) -> None:
        """Called whenever two orders match. Could be one of your orders, or two other people's orders.
        Parameters
        ----------
        ticker
            Ticker of orders that were matched
        side:
            Side of orders that were matched
        quantity
            Volume traded
        price
            Price that trade was executed at
        """
        self.ticker = ticker
        self.last_traded_price = price

    def on_orderbook_update(
        self, ticker: Ticker, side: Side, quantity: float, price: float
    ) -> None:
        """Called whenever the orderbook changes. This could be because of a trade, or because of a new order, or both.
        Parameters
        ----------
        ticker
            Ticker that has an orderbook update
        side
            Which orderbook was updated
        price
            Price of orderbook that has an update
        quantity
            Volume placed into orderbook
        """

    def on_account_update(
        self,
        ticker: Ticker,
        side: Side,
        price: float,
        quantity: float,
        capital_remaining: float,
    ) -> None:
        """Called whenever one of your orders is filled.
        Parameters
        ----------
        ticker
            Ticker of order that was fulfilled
        side
            Side of order that was fulfilled
        price
            Price that order was fulfilled at
        quantity
            Volume of order that was fulfilled
        capital_remaining
            Amount of capital after fulfilling order
        """
        mult = 2*(side==Side(0))-1
        self.delta += mult * quantity

    def on_game_event_update(self,
                           event_type: str,
                           home_away: str,
                           home_score: int,
                           away_score: int,
                           player_name: Optional[str],
                           substituted_player_name: Optional[str],
                           shot_type: Optional[str],
                           assist_player: Optional[str],
                           rebound_type: Optional[str],
                           coordinate_x: Optional[float],
                           coordinate_y: Optional[float],
                           time_seconds: Optional[float]
        ) -> None:
        """Called whenever a basketball game event occurs.
        Parameters
        ----------
        event_type
            Type of event that occurred
        home_score
            Home team score after event
        away_score
            Away team score after event
        player_name (Optional)
            Player involved in event
        substituted_player_name (Optional)
            Player being substituted out
        shot_type (Optional)
            Type of shot
        assist_player (Optional)
            Player who made the assist
        rebound_type (Optional)
            Type of rebound
        coordinate_x (Optional)
            X coordinate of shot location in feet
        coordinate_y (Optional)
            Y coordinate of shot location in feet
        time_seconds (Optional)
            Game time remaining in seconds
        """
        self.away_score = away_score
        self.home_score = home_score
        self.time_left = time_seconds

        if (self.my_ask_id):
            cancel_order(self.my_ask_id)
        if (self.my_bid_id):
            cancel_order(self.my_bid_id)
        if self.ticker:
            bid = self.fair()-self.edge
            ask = self.fair()+self.edge
            place_limit_order(Side(0), self.ticker, 1, bid)
            place_limit_order(Side(1), self.ticker, 1, ask)        
            print(f"Score: {home_score} - {away_score}")
            print(f"Market: {bid} @ {ask}")
            print(f"last trade @ {self.last_traded_price}")
            print(f"delta: {self.delta}")

        if event_type == "END_GAME":
            # IMPORTANT: Highly recommended to call reset_state() when the
            # game ends. See reset_state() for more details.
            print(f"expected pnl: {self.cumTrades * self.edge}")
            self.reset_state()
            return

