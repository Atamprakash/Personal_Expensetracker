import matplotlib.pyplot as plt
import pandas as pd
from prophet import Prophet
from database import fetch_all_transactions


def prepare_data():
    data = fetch_all_transactions()
    df = pd.DataFrame(data, columns=["date", "type", "amount", "description", "category"])

    # Filter for expenses only
    df = df[df["type"] == "Expense"]

    # Rename columns for Prophet
    df = df[["date", "amount"]].rename(columns={"date": "ds", "y": "amount"})
    df["ds"] = pd.to_datetime(df["ds"])
    df["y"] = pd.to_numeric(df["amount"], errors="coerce")
    df.dropna(subset=["ds", "y"], inplace=True)

    return df


def train_model(df):
    model = Prophet()
    model.fit(df)
    return model


def make_predictions(model, periods=30):
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    return forecast


def plot_forecast(model, forecast):
    # Forecast Plot with Custom Legend
    fig1 = model.plot(forecast)

    # Custom legend
    plt.legend([
        "Historical Data (Black Dots)",
        "Forecast (Blue Line)",
        "Confidence Interval (Shaded)"
    ], loc="upper left", fontsize=9)

    plt.title("Expense Forecast", fontsize=14, fontweight='bold')
    plt.xlabel("Date")
    plt.ylabel("Expense Amount (₹)")
    plt.tight_layout()
    plt.show()

    # Components plot: Trend, Weekly & Yearly seasonality
    fig2 = model.plot_components(forecast)
    plt.tight_layout()
    plt.show()
