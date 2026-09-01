from openchart import NSEData
import datetime

nse = NSEData()

end_date = datetime.datetime.now()
start_date = end_date - datetime.timedelta(days=5)

# Fetch 5-minute historical data for RELIANCE-EQ
data = nse.historical(
    symbol='RELIANCE-EQ',
    segment='EQ',
    start=start_date,
    end=end_date,
    interval='5m'
)

if not data.empty:
    print("5-minute historical data for RELIANCE-EQ (Last 5 days):")
    print(data)
else:
    print("No data available for RELIANCE-EQ for the specified time period.")
