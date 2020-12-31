from wetterdienst.dwd.forecasts.metadata.dates import DWDForecastDate
from wetterdienst.dwd.forecasts import DWDMosmixData, DWDMosmixType
from wetterdienst.util.cli import setup_logging

from math import sin, radians

# for plotting
import matplotlib.pyplot as plt

# parameter
pvArea = 10.0
timeScale = 1.0
efficiencyFactor = 0.1
inclinationFactor = sin(radians(30))
factor = efficiencyFactor * inclinationFactor * pvArea / timeScale

mosmix = DWDMosmixData(
        station_ids=["10515"], # 10515 = Koblenz-Bend.
        parameters=["Rad1h"], # Rad1h = Global Irradiance
        start_issue=DWDForecastDate.LATEST,  # automatically set if left empty
        mosmix_type=DWDMosmixType.SMALL,
        tidy_data=True,
        humanize_parameters=True,
    )

# fetch MOSMIX forecast
response = next(mosmix.query())

# calculate power from global irradiance
response.data['VALUE'] *= factor

# plot 24h forecast
response.data.iloc[:24].plot(x='DATE', y='VALUE')
plt.xlabel('Time')
plt.ylabel('Power in W')
plt.title('PV Power Forecast 24h')
plt.show()

# SQL database
mydb = mysql.connector.connect(
    host="localhost",
    user="forecast-user",
    password="2mwDNv7MkPPp9qyP",
    database="smartmeter"
    )
mycursor = mydb.cursor()

# empty last forecast database
sql = "TRUNCATE `smartmeter`.`forecast`"
mycursor.execute(sql)
mydb.commit()

# upload current forecast into database
sql = "INSERT INTO forecast (date, power) VALUES (%s, %s)"
val = (response.data['DATE'], response.data['VALUE'])
mycursor.execute(sql, val)
mydb.commit()
