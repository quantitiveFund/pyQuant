# Acceleration Bands (ABANDS)



### 描述

Price Headley's Acceleration Bands serve as a trading envelope that  factor in a stock's typical volatility over standard settings of 20 or 80 bars.  They can be used across any time frame, from intra-day to weekly and monthly time frames.  We look for breakout indicators outside these bands, while also using the shorter time frames to define likely support and resistance levels at the lower and upper Acceleration Bands. Acceleration Bands are plotted around a simple moving average as the midpoint, and the upper and lower bands are of equal distance from this midpoint.

Acceleration Bands principal use is in finding the acceleration in currency pair price and benefit as long as this acceleration preserves.

![](http://forex-indicators.net/files/indicators/acceleration_bands.png)

Acceleration bands are set as an envelope around a **20** period simple moving average on equal distance from it. 

Headley, the inventor of Acceleration Bands indicator suggests using them on weekly and monthly time frames to determine price acceleration breakouts (breakouts outside the bands).

When Acceleration Bands are used for smaller time frames, upper and lower bands are treated as levels of possible support and resistance.

The Acceleration bands are based on the average trading range for each day. The values are plotted equidistant from an n-day simple moving average which serves as the center or middle band. The author indicates that successive days exceeding one of the bands tends to indicate an entry point.

Because the bands use the daily trading range (high-low) they will also expand and contract based on the volatility of the price.

Rule of acceleration bands trading:

1) Two consecutive closes outside the acceleration bands.

2) Trade with a tight stop.

3) It has been watched that acceleration bands are specifically useful in trading options.



![60%](https://i1.wp.com/stockmaniacs.net/images/Acceleration-Bands-Trading.png)



### 参考文献

1. [Catching Big Trends with Acceleration Bands](https://www.bigtrends.com/education/catching-big-trends-with-acceleration-bands/) by Price Headley
2. [forex-indicators](http://forex-indicators.net/acceleration-bands)
3. [StockFetcher](https://www.stockfetcher.com/forums/Indicators/Acceleration-Bands/32186)
4. [StockManiacs](https://www.stockmaniacs.net/acceleration-bands-trading-new-way-trade-options/)
5. [Youtube](https://www.youtube.com/watch?v=7Be_kiZXiYw)

### 公式

The width of the bands is based on the formula below.

Upper Band = Simple Moving Average (High * ( 1 + 4 * (High - Low) / (High + Low)))

Middle Band = Simple Moving Average

Lower Band = Simple Moving Average (Low * (1 - 4 * (High - Low)/ (High + Low)))

### 代码

```python
def abands(dat, lag = 10):
    mb = dat[['Close']].rolling(window = lag).mean()
    hi = dat[['High']]
    hi.columns=['p']
    lo = dat[['Low']]
    lo.columns=['p']
    ub = hi.mul(1 + 4 * (hi.sub(lo)).div(hi.add(lo)))
    lb = lo.mul(1 - 4 * (hi.sub(lo)).div(hi.add(lo)))
    ub = ub.rolling(window = lag).mean()
    lb = lb.rolling(window = lag).mean() 
    return mb, ub, lb
```

### 回测

