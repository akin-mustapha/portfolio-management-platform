"""
  Func Module
"""
import pandas as pd
import numpy as np

class FuncAssetDerivedMetric:
  @classmethod
  def run(cls, data):
    df = pd.DataFrame(data)
    df['pct_drawdown'] = (df['price'] - df['recent_high_30d']) / df['recent_high_30d']
    df['price_vs_ma_50'] = np.where(
        df['ma_50'] != 0,
        (df['price'] - df['ma_50']) / df['ma_50'],
        None
      )
    df['norm_price_30d'] = (df['recent_high_30d'] - df['recent_low_30d']) / df['ma_30']
    df['volatility_30d'] = (
        df.groupby('asset_id')['price']
          .pct_change()
          .rolling(30)
          .std()
      )
    df['dca_bias'] = (
        -0.5 * df['pct_drawdown']
        -0.4 * df['price_vs_ma_50']
        +0.1 * df['volatility_30d']
    )
    df = df.drop(['price'], axis=1)
    return df


class FuncSilverAssetA:
  @classmethod
  def run(cls, data):
    df = pd.DataFrame(data)
    df['pct_drawdown'] = (df['price'] - df['recent_high_30d']) / df['recent_high_30d']
    df['price_vs_ma_50'] = np.where(
        df['ma_50'] != 0,
        (df['price'] - df['ma_50']) / df['ma_50'],
        None
      )
    df['norm_price_30d'] = (df['recent_high_30d'] - df['recent_low_30d']) / df['ma_30']
    df['volatility_30d'] = (
        df.groupby('asset_id')['price']
          .pct_change()
          .rolling(30)
          .std()
      )
    df['dca_bias'] = (
        -0.5 * df['pct_drawdown']
        -0.4 * df['price_vs_ma_50']
        +0.1 * df['volatility_30d']
    )
    df = df.drop(['price'], axis=1)
    return df
