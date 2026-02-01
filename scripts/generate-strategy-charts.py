# -*- coding: utf-8 -*-
"""
전략별 캔들+거래량 차트 생성: 익절(tp)·손절(sl) 두 케이스씩.
실행: python scripts/generate-strategy-charts.py
출력: assets/images/stock/strategy-*-tp.png, strategy-*-sl.png (7×2=14개)
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# 한글 폰트 설정 (Windows: 맑은 고딕)
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

try:
    import mplfinance as mpf
except ImportError:
    print("mplfinance 필요: pip install mplfinance")
    raise

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
OUT_DIR = os.path.join(REPO_ROOT, "assets", "images", "stock")
os.makedirs(OUT_DIR, exist_ok=True)

N = 10
dates = pd.date_range("2025-01-01", periods=N, freq="D")


def trend_bars(entry_idx, exit_idx, n, is_tp):
    """진입~청산 구간만 상승(1) 또는 하락(-1), 나머지 0(랜덤)."""
    t = [0] * n
    for i in range(entry_idx, min(exit_idx + 1, n)):
        t[i] = 1 if is_tp else -1
    return t


def make_ohlcv(open_prices, volumes=None, bar_trend=None):
    """시가 배열로 O,H,L,C,V DataFrame 생성. bar_trend: 봉별 방향 1=상승봉, -1=하락봉, None=랜덤."""
    o = np.asarray(open_prices, dtype=float)
    n = len(o)
    h = np.empty(n)
    l = np.empty(n)
    c = np.empty(n)
    for i in range(n):
        t = bar_trend[i] if bar_trend is not None and i < len(bar_trend) else None
        if t == 1:  # 상승봉: 종가 > 시가
            move = 150 + np.abs(np.random.randn()) * 200
            c[i] = o[i] + move
            h[i] = c[i] + np.abs(np.random.randn()) * 100
            l[i] = o[i] - np.abs(np.random.randn()) * 80
        elif t == -1:  # 하락봉: 종가 < 시가
            move = 150 + np.abs(np.random.randn()) * 200
            c[i] = o[i] - move
            l[i] = c[i] - np.abs(np.random.randn()) * 100
            h[i] = o[i] + np.abs(np.random.randn()) * 80
        else:
            c[i] = o[i] + (np.random.randn() * 200)
            h[i] = o[i] + np.abs(np.random.randn() * 300)
            l[i] = o[i] - np.abs(np.random.randn() * 300)
        h[i] = max(h[i], o[i], c[i], l[i])
        l[i] = min(l[i], o[i], c[i], h[i])
    if volumes is None:
        volumes = np.random.randint(80, 120, n) * 10000
    df = pd.DataFrame({"Open": o, "High": h, "Low": l, "Close": c, "Volume": volumes}, index=dates[:n])
    df.index.name = "Date"
    return df


mc = mpf.make_marketcolors(
    up="#2962FF",  # 상승 파란색
    down="#FF5252",  # 하락 빨간색
    edge="inherit",
    wick="inherit",
    volume={"up": "#2962FF", "down": "#FF5252"},
)
s = mpf.make_mpf_style(
    marketcolors=mc,
    gridstyle="-",
    gridcolor="#E0E0E0",
    facecolor="white",
    figcolor="white",
    rc={
        "patch.linewidth": 1.5,
        "lines.linewidth": 1.8,
        "font.size": 12,
        "axes.titlesize": 16,
        "axes.titleweight": "bold",
        "axes.labelsize": 11,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
    },
)


# ----- 1. 돌파 (Breakout): 저항선·지지선 -----
def gen_breakout_tp():
    base = 55000
    opens = [base + np.random.randn() * 150 for _ in range(5)]
    resistance = max(opens) + 100
    support = min(opens) - 80
    opens.extend([resistance - 80, resistance + 400])
    for _ in range(N - 7):
        opens.append(opens[-1] + np.random.randn() * 120 + 80)
    vol = [100] * 5 + [280, 300] + [120] * (N - 7)
    entry, exit_ = 6, 8
    df = make_ohlcv(opens, np.array(vol) * 10000, trend_bars(entry, exit_, N, True))
    entry_price = df["Close"].iloc[entry]
    channel_height = resistance - support
    target_price = entry_price + channel_height  # 패턴 높이만큼 투영
    stop_loss = resistance - (resistance - support) * 0.1  # 저항선 바로 아래
    return df, entry, exit_, {"resistance": resistance, "support": support, "entry_price": entry_price, "target_price": target_price, "stop_loss": stop_loss, "is_tp": True}


def gen_breakout_sl():
    base = 55000
    opens = [base + np.random.randn() * 150 for _ in range(5)]
    resistance = max(opens) + 100
    support = min(opens) - 80
    opens.extend([resistance - 80, resistance + 400])
    opens.append(opens[-1] - 350)
    opens.append(opens[-1] - 200)
    for _ in range(N - 9):
        opens.append(opens[-1] + np.random.randn() * 80 - 30)
    vol = [100] * 5 + [280, 300] + [150, 120] + [100] * (N - 9)
    entry, exit_ = 6, 7
    df = make_ohlcv(opens, np.array(vol) * 10000, trend_bars(entry, exit_, N, False))
    entry_price = df["Close"].iloc[entry]
    stop_loss = resistance - (resistance - support) * 0.1  # 저항선 바로 아래
    return df, entry, exit_, {"resistance": resistance, "support": support, "entry_price": entry_price, "stop_loss": stop_loss, "is_tp": False}


# ----- 2. 갭 (Gap): 갭 구간(전일 종가~당일 시가) -----
def gen_gap_tp():
    base = 52000
    opens = [base + i * 60 + np.random.randn() * 80 for i in range(4)]
    gap_bottom = opens[-1]
    opens.append(opens[-1] + 900)
    gap_top = opens[-1]
    for _ in range(N - 5):
        opens.append(opens[-1] + np.random.randn() * 100)
    entry, exit_ = 4, 7
    df = make_ohlcv(opens, bar_trend=trend_bars(entry, exit_, N, True))
    entry_price = df["Close"].iloc[entry]
    gap_size = gap_top - gap_bottom
    target_price = entry_price + gap_size * 1.5  # R:R 1:1.5
    stop_loss = gap_bottom  # 갭 저점 아래
    return df, entry, exit_, {"gap_bottom": gap_bottom, "gap_top": gap_top, "entry_price": entry_price, "target_price": target_price, "stop_loss": stop_loss, "is_tp": True}


def gen_gap_sl():
    base = 52000
    opens = [base + i * 60 + np.random.randn() * 80 for i in range(4)]
    gap_bottom = opens[-1]
    opens.append(opens[-1] + 900)
    gap_top = opens[-1]
    opens.append(opens[-1] - 400)
    opens.append(opens[-1] - 200)
    for _ in range(N - 7):
        opens.append(opens[-1] + np.random.randn() * 60 - 50)
    entry, exit_ = 4, 5
    df = make_ohlcv(opens, bar_trend=trend_bars(entry, exit_, N, False))
    entry_price = df["Close"].iloc[entry]
    stop_loss = gap_bottom  # 갭 저점 아래
    return df, entry, exit_, {"gap_bottom": gap_bottom, "gap_top": gap_top, "entry_price": entry_price, "stop_loss": stop_loss, "is_tp": False}


# ----- 3. 모멘텀: 추세선(저점 연결) -----
def gen_momentum_tp():
    base = 50000
    opens = [base]
    for i in range(N - 1):
        opens.append(opens[-1] + 150 + np.random.randn() * 100)
    entry, exit_ = 3, 7
    df = make_ohlcv(opens, bar_trend=trend_bars(entry, exit_, N, True))
    # 추세선: 구간 내 저점들을 이은 직선 근사 (시작~끝 저점)
    trend_low = pd.Series([df["Low"].iloc[0], df["Low"].iloc[-1]], index=[df.index[0], df.index[-1]]).reindex(df.index).interpolate()
    entry_price = df["Close"].iloc[entry]
    atr = (df["High"] - df["Low"]).mean()  # 간단한 ATR 근사
    target_price = entry_price + atr * 2  # ATR 2배 목표
    stop_loss = df["Low"].iloc[entry - 1] if entry > 0 else entry_price - atr  # 직전 저점
    return df, entry, exit_, {"trend_line": trend_low, "entry_price": entry_price, "target_price": target_price, "stop_loss": stop_loss, "is_tp": True}


def gen_momentum_sl():
    base = 50000
    opens = [base, base + 200, base + 350]
    for _ in range(N - 3):
        opens.append(opens[-1] - 80 + np.random.randn() * 60)
    entry, exit_ = 3, 5
    df = make_ohlcv(opens, bar_trend=trend_bars(entry, exit_, N, False))
    trend_low = pd.Series([df["Low"].iloc[0], df["Low"].iloc[-1]], index=[df.index[0], df.index[-1]]).reindex(df.index).interpolate()
    entry_price = df["Close"].iloc[entry]
    atr = (df["High"] - df["Low"]).mean()
    stop_loss = df["Low"].iloc[entry - 1] if entry > 0 else entry_price - atr
    return df, entry, exit_, {"trend_line": trend_low, "entry_price": entry_price, "stop_loss": stop_loss, "is_tp": False}


# ----- 4. 거래량 급증: 스파이크 구간 강조(진입 직전 = 스파이크 봉) -----
def gen_volume_spike_tp():
    base = 54000
    opens = [base + np.random.randn() * 150 for _ in range(4)]
    opens.append(opens[-1] + 500)
    opens.extend([opens[-1] + np.random.randn() * 100 for _ in range(N - 5)])
    vol = [100] * 4 + [450] + [110] * (N - 5)
    entry, exit_ = 4, 7
    df = make_ohlcv(opens, np.array(vol) * 10000, trend_bars(entry, exit_, N, True))
    entry_price = df["Close"].iloc[entry]
    spike_low = df["Low"].iloc[entry]
    risk = entry_price - spike_low
    target_price = entry_price + risk * 2  # R:R 1:2
    stop_loss = spike_low - 50  # 스파이크 봉 저점 아래
    return df, entry, exit_, {"spike_idx": 4, "entry_price": entry_price, "target_price": target_price, "stop_loss": stop_loss, "is_tp": True}


def gen_volume_spike_sl():
    base = 54000
    opens = [base + np.random.randn() * 150 for _ in range(4)]
    opens.append(opens[-1] + 500)
    opens.append(opens[-1] - 450)
    opens.extend([opens[-1] + np.random.randn() * 80 - 40 for _ in range(N - 6)])
    vol = [100] * 4 + [450, 200] + [100] * (N - 6)
    entry, exit_ = 4, 5
    df = make_ohlcv(opens, np.array(vol) * 10000, trend_bars(entry, exit_, N, False))
    entry_price = df["Close"].iloc[entry]
    spike_low = df["Low"].iloc[entry]
    stop_loss = spike_low - 50
    return df, entry, exit_, {"spike_idx": 4, "entry_price": entry_price, "stop_loss": stop_loss, "is_tp": False}


# ----- 5. VWAP: VWAP선(거래량 가중 평균) -----
def _vwap_series(df):
    typical = (df["High"] + df["Low"] + df["Close"]) / 3
    return (typical * df["Volume"]).cumsum() / df["Volume"].cumsum()


def gen_vwap_tp():
    base = 53000
    opens = [base, base + 250, base + 100, base + 400, base + 300]
    for _ in range(N - 5):
        opens.append(opens[-1] + np.random.randn() * 100)
    entry, exit_ = 3, 6
    df = make_ohlcv(opens, bar_trend=trend_bars(entry, exit_, N, True))
    vwap = _vwap_series(df)
    entry_price = df["Close"].iloc[entry]
    vwap_at_entry = vwap.iloc[entry]
    # VWAP 기준 ±1 표준편차 근사
    price_std = df["Close"].std()
    target_price = vwap_at_entry + price_std  # 상단 편차 밴드
    stop_loss = vwap_at_entry - price_std * 0.3  # VWAP 약간 아래
    return df, entry, exit_, {"vwap": vwap, "entry_price": entry_price, "target_price": target_price, "stop_loss": stop_loss, "is_tp": True}


def gen_vwap_sl():
    base = 53000
    opens = [base, base + 250, base + 100, base + 400, base + 300]
    opens.append(opens[-1] - 350)
    opens.extend([opens[-1] + np.random.randn() * 60 - 30 for _ in range(N - 6)])
    entry, exit_ = 3, 5
    df = make_ohlcv(opens, bar_trend=trend_bars(entry, exit_, N, False))
    vwap = _vwap_series(df)
    entry_price = df["Close"].iloc[entry]
    vwap_at_entry = vwap.iloc[entry]
    price_std = df["Close"].std()
    stop_loss = vwap_at_entry - price_std * 0.3
    return df, entry, exit_, {"vwap": vwap, "entry_price": entry_price, "stop_loss": stop_loss, "is_tp": False}


# ----- 6. 평균 회귀: 이동평균선 -----
def gen_mean_reversion_tp():
    base = 55000
    opens = [base + np.random.randn() * 150 for _ in range(3)]
    for _ in range(3):
        opens.append(opens[-1] + 250 + np.random.randn() * 80)
    for _ in range(N - 6):
        opens.append(opens[-1] - 100 + np.random.randn() * 80)
    entry, exit_ = 6, 9
    df = make_ohlcv(opens, bar_trend=trend_bars(entry, exit_, N, True))
    ma = df["Close"].rolling(3, min_periods=1).mean()
    entry_price = df["Close"].iloc[entry]
    ma_at_entry = ma.iloc[entry]
    atr = (df["High"] - df["Low"]).mean()
    target_price = ma_at_entry  # 이동평균 복귀가 목표
    stop_loss = df["High"].iloc[:entry].max() + atr * 0.5  # 스윙 고점 + 버퍼 (넓게)
    return df, entry, exit_, {"ma": ma, "entry_price": entry_price, "target_price": target_price, "stop_loss": stop_loss, "is_tp": True}


def gen_mean_reversion_sl():
    base = 55000
    opens = [base + np.random.randn() * 150 for _ in range(3)]
    for _ in range(3):
        opens.append(opens[-1] + 250 + np.random.randn() * 80)
    for _ in range(N - 6):
        opens.append(opens[-1] - 50 + np.random.randn() * 60)
    entry, exit_ = 6, 8
    df = make_ohlcv(opens, bar_trend=trend_bars(entry, exit_, N, False))
    ma = df["Close"].rolling(3, min_periods=1).mean()
    entry_price = df["Close"].iloc[entry]
    atr = (df["High"] - df["Low"]).mean()
    stop_loss = df["High"].iloc[:entry].max() + atr * 0.5
    return df, entry, exit_, {"ma": ma, "entry_price": entry_price, "stop_loss": stop_loss, "is_tp": False}


# ----- 7. ORB: 시초가 범위(고가·저가) -----
def gen_orb_tp():
    base = 54500
    opens = [base + np.random.randn() * 120 for _ in range(3)]
    orb_range_high = base + 280
    opens.append(orb_range_high)
    for _ in range(N - 4):
        opens.append(opens[-1] + np.random.randn() * 80 + 50)
    entry, exit_ = 3, 7
    df = make_ohlcv(opens, bar_trend=trend_bars(entry, exit_, N, True))
    orb_high = df["High"].iloc[:4].max()
    orb_low = df["Low"].iloc[:4].min()
    orb_range = orb_high - orb_low
    entry_price = df["Close"].iloc[entry]
    target_price = orb_high + orb_range * 1.5  # 손절 거리의 1.5배
    stop_loss = orb_low  # 범위 반대쪽 끝 (보수적)
    return df, entry, exit_, {"orb_high": orb_high, "orb_low": orb_low, "entry_price": entry_price, "target_price": target_price, "stop_loss": stop_loss, "is_tp": True}


def gen_orb_sl():
    base = 54500
    opens = [base + np.random.randn() * 120 for _ in range(3)]
    opens.append(base + 280)
    opens.append(opens[-1] - 350)
    opens.extend([opens[-1] + np.random.randn() * 60 - 20 for _ in range(N - 5)])
    entry, exit_ = 3, 4
    df = make_ohlcv(opens, bar_trend=trend_bars(entry, exit_, N, False))
    orb_high = df["High"].iloc[:4].max()
    orb_low = df["Low"].iloc[:4].min()
    entry_price = df["Close"].iloc[entry]
    stop_loss = orb_low
    return df, entry, exit_, {"orb_high": orb_high, "orb_low": orb_low, "entry_price": entry_price, "stop_loss": stop_loss, "is_tp": False}


def save_chart(df, entry_idx, exit_idx, filename, title, strategy_slug="", extra=None):
    path = os.path.join(OUT_DIR, filename)
    kwargs = dict(
        type="candle",
        style=s,
        volume=True,
        title=f"\n{title}\n",
        figsize=(12, 7),
        datetime_format="%d",
        xrotation=0,
        tight_layout=True,
        scale_padding={"left": 0.5, "right": 1.0, "top": 1.5, "bottom": 0.5},
        returnfig=True,
    )
    addplots = []
    vline_dates = []
    vline_colors = []
    price_range = df["High"].max() - df["Low"].min()
    offset = price_range * 0.025  # 마커가 차트 밖으로 나가지 않도록 줄임

    # 실제 진입가/청산가 가져오기
    entry_price = extra.get("entry_price", df["Close"].iloc[entry_idx]) if extra and entry_idx is not None else None
    is_tp = extra.get("is_tp", True) if extra else True

    # 매수 마커: 진입가 위쪽에 표시
    if entry_idx is not None and 0 <= entry_idx < len(df) and entry_price is not None:
        entry_marker = pd.Series(index=df.index, dtype=float)
        entry_marker.iloc[entry_idx] = entry_price + offset
        addplots.append(mpf.make_addplot(entry_marker, type="scatter", marker="^", markersize=120, color="#00C853"))

    # 매도 마커: 실제 청산 캔들 기준으로 표시 (차트 밖으로 나가지 않도록)
    if exit_idx is not None and 0 <= exit_idx < len(df):
        exit_marker = pd.Series(index=df.index, dtype=float)
        if is_tp:
            # 익절: 청산 캔들의 High 위에 표시
            exit_marker.iloc[exit_idx] = df["High"].iloc[exit_idx] + offset
        else:
            # 손절: 청산 캔들의 Low 아래에 표시
            exit_marker.iloc[exit_idx] = df["Low"].iloc[exit_idx] - offset
        addplots.append(mpf.make_addplot(exit_marker, type="scatter", marker="v", markersize=120, color="#D50000"))

    # 공통: 진입가/목표가/손절가 라인 (진입 시점 이후만 표시)
    if extra:
        start_idx = entry_idx if entry_idx is not None else 0
        if "entry_price" in extra:
            entry_line = pd.Series(index=df.index, dtype=float)
            entry_line.iloc[start_idx:] = extra["entry_price"]
            addplots.append(mpf.make_addplot(entry_line, color="#1976D2", linestyle="-", width=2.5, alpha=0.85))
        if "target_price" in extra and extra.get("is_tp", False):
            target_line = pd.Series(index=df.index, dtype=float)
            target_line.iloc[start_idx:] = extra["target_price"]
            addplots.append(mpf.make_addplot(target_line, color="#00C853", linestyle="-", width=3, alpha=0.95))
        if "stop_loss" in extra:
            sl_line = pd.Series(index=df.index, dtype=float)
            sl_line.iloc[start_idx:] = extra["stop_loss"]
            addplots.append(mpf.make_addplot(sl_line, color="#D50000", linestyle="-", width=3, alpha=0.95))

    # 전략별 오버레이
    if extra:
        if strategy_slug == "breakout":
            if "resistance" in extra:
                addplots.append(mpf.make_addplot(pd.Series(extra["resistance"], index=df.index), color="#B71C1C", linestyle="--", width=2))
            if "support" in extra:
                addplots.append(mpf.make_addplot(pd.Series(extra["support"], index=df.index), color="#1B5E20", linestyle="--", width=2))
        elif strategy_slug == "gap":
            if "gap_bottom" in extra:
                addplots.append(mpf.make_addplot(pd.Series(extra["gap_bottom"], index=df.index), color="#757575", linestyle="--", width=1.8))
            if "gap_top" in extra:
                addplots.append(mpf.make_addplot(pd.Series(extra["gap_top"], index=df.index), color="#757575", linestyle="--", width=1.8))
        elif strategy_slug == "momentum" and "trend_line" in extra:
            addplots.append(mpf.make_addplot(extra["trend_line"], color="#7B1FA2", linestyle="-", width=2))
        elif strategy_slug == "volume-spike" and "spike_idx" in extra:
            idx = extra["spike_idx"]
            if 0 <= idx < len(df):
                vline_dates.append(df.index[idx])
                vline_colors.append("#FF6F00")
        elif strategy_slug == "vwap" and "vwap" in extra:
            addplots.append(mpf.make_addplot(extra["vwap"], color="#00838F", linestyle="-", width=2.5))
        elif strategy_slug == "mean-reversion" and "ma" in extra:
            addplots.append(mpf.make_addplot(extra["ma"], color="#E65100", linestyle="-", width=2))
        elif strategy_slug == "orb":
            if "orb_high" in extra:
                addplots.append(mpf.make_addplot(pd.Series(extra["orb_high"], index=df.index), color="#1A237E", linestyle="--", width=2))
            if "orb_low" in extra:
                addplots.append(mpf.make_addplot(pd.Series(extra["orb_low"], index=df.index), color="#1A237E", linestyle="--", width=2))

    if vline_dates:
        kwargs["vlines"] = dict(vlines=vline_dates, linewidths=2, colors=vline_colors, alpha=0.8, linestyle="--")
    if addplots:
        kwargs["addplot"] = addplots
    fig, axes = mpf.plot(df, **kwargs)
    ax = axes[0]  # 메인 가격 차트 축

    # 텍스트 라벨 추가
    text_offset = price_range * 0.05  # 마커가 차트 밖으로 나가지 않도록 줄임
    font_props = {"fontname": "Malgun Gothic", "fontsize": 12, "fontweight": "bold"}

    # entry/exit이 가까울 때 수평 오프셋 적용
    h_offset = 0.3 if (entry_idx is not None and exit_idx is not None and abs(exit_idx - entry_idx) <= 2) else 0

    if entry_idx is not None and 0 <= entry_idx < len(df) and entry_price is not None:
        ax.annotate(
            "매수",
            xy=(entry_idx, entry_price + offset),
            xytext=(entry_idx - h_offset, entry_price + text_offset),
            color="#00C853",
            ha="center",
            va="bottom",
            **font_props,
        )
    if exit_idx is not None and 0 <= exit_idx < len(df):
        if is_tp:
            # 익절: 청산 캔들의 High 위에 표시
            exit_y = df["High"].iloc[exit_idx] + offset
            label_y = df["High"].iloc[exit_idx] + text_offset
            va_align = "bottom"
        else:
            # 손절: 청산 캔들의 Low 아래에 표시
            exit_y = df["Low"].iloc[exit_idx] - offset
            label_y = df["Low"].iloc[exit_idx] - text_offset
            va_align = "top"
        ax.annotate(
            "매도",
            xy=(exit_idx, exit_y),
            xytext=(exit_idx + h_offset, label_y),
            color="#D50000",
            ha="center",
            va=va_align,
            **font_props,
        )

    fig.savefig(path, dpi=150, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)
    print("Saved:", path)


def main():
    strategies = [
        ("breakout", "Breakout", gen_breakout_tp, gen_breakout_sl),
        ("gap", "Gap", gen_gap_tp, gen_gap_sl),
        ("momentum", "Momentum", gen_momentum_tp, gen_momentum_sl),
        ("volume-spike", "Volume Spike", gen_volume_spike_tp, gen_volume_spike_sl),
        ("vwap", "VWAP", gen_vwap_tp, gen_vwap_sl),
        ("mean-reversion", "Mean Reversion", gen_mean_reversion_tp, gen_mean_reversion_sl),
        ("orb", "ORB", gen_orb_tp, gen_orb_sl),
    ]
    for slug, title, gen_tp, gen_sl in strategies:
        df, e, x, extra_tp = gen_tp()
        save_chart(df, e, x, f"strategy-{slug}-tp.png", f"{title} (Take Profit)", strategy_slug=slug, extra=extra_tp)
        df, e, x, extra_sl = gen_sl()
        save_chart(df, e, x, f"strategy-{slug}-sl.png", f"{title} (Stop Loss)", strategy_slug=slug, extra=extra_sl)
    print("Done. 14 charts (7 strategies x 2 cases) in", OUT_DIR)


if __name__ == "__main__":
    main()
