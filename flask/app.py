from flask import Flask, request
from os import environ
from entsoe import EntsoeRawClient
from datetime import datetime, date, timedelta
from entsoe.mappings import lookup_area
import pandas as pd
import json
import jq
import xmltodict

app = Flask(__name__)

# https://github.com/EnergieID/entsoe-py
entsoe_api_key = environ.get('entsoe_api_key')
entsoe_start = environ.get('entsoe_start') or 25
entsoe_end = environ.get('entsoe_end') or 24

@app.route('/metrics', methods=['GET'])
def metrics():
    #######################################
    # Create Entsoe client with API key
    #######################################
    client = EntsoeRawClient(api_key=entsoe_api_key)
    # Compute the time window from yesterday within 1 hour
    today = datetime.today()
    TwentyFour = (today - timedelta(hours = int(entsoe_end) ))
    TwentyFive = (today - timedelta(hours = int(entsoe_start) ))
    start = pd.Timestamp(TwentyFive, tz='Europe/Berlin')
    end = pd.Timestamp(TwentyFour, tz='Europe/Berlin')
    # Relates country is Germany
    country_code = 'DE'
    
    #######################################
    # Query all energy generation in this time window for this country
    #######################################
    try:
        df_generation = client.query_generation(country_code, start=start,end=end, nett=True)
        data_dict = xmltodict.parse(df_generation)
    except:
        message = "No data from API"
        return message, 500, {'Content-Type': 'text/plain'}
    
    #######################################
    # Filter Biomass
    # ref: https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html#_psrtype
    #######################################
    try:
        filter_b01 = jq.compile('.GL_MarketDocument.TimeSeries[] | select(.MktPSRType.psrType == "B01") | .Period.Point[0].quantity')
        result_b01 = filter_b01.input(data_dict).first()
    except:
        result_b01=0
    #######################################
    # Filter Fossil Brown coal/Lignite
    #######################################
    try:
        filter_b02 = jq.compile('.GL_MarketDocument.TimeSeries[] | select(.MktPSRType.psrType == "B02") | .Period.Point[0].quantity')
        result_b02 = filter_b02.input(data_dict).first()
    except:
        result_b02=0
    #######################################
    # Filter Fossil Gas
    #######################################
    try:
        filter_b04 = jq.compile('.GL_MarketDocument.TimeSeries[] | select(.MktPSRType.psrType == "B04") | .Period.Point[0].quantity')
        result_b04 = filter_b04.input(data_dict).first()
    except:
        result_b04=0
    #######################################
    # Filter Fossil Hard coal
    #######################################
    try:
        filter_b05 = jq.compile('.GL_MarketDocument.TimeSeries[] | select(.MktPSRType.psrType == "B05") | .Period.Point[0].quantity')
        result_b05 = filter_b05.input(data_dict).first()
    except:
        result_b05=0
    #######################################
    # Filter Geothermal
    #######################################
    try:
        filter_b09 = jq.compile('.GL_MarketDocument.TimeSeries[] | select(.MktPSRType.psrType == "B09") | .Period.Point[0].quantity')
        result_b09 = filter_b09.input(data_dict).first()
    except:
        result_b09=0
    #######################################
    # Filter Hydro Pumped Storage
    #######################################
    try:
        filter_b10 = jq.compile('.GL_MarketDocument.TimeSeries[] | select(.MktPSRType.psrType == "B10") | .Period.Point[0].quantity')
        result_b10 = filter_b10.input(data_dict).first()
    except:
        result_b10=0
    #######################################
    # Filter Hydro Run-over-river and poundage
    #######################################
    try:
        filter_b11 = jq.compile('.GL_MarketDocument.TimeSeries[] | select(.MktPSRType.psrType == "B11") | .Period.Point[0].quantity')
        result_b11 = filter_b11.input(data_dict).first()
    except:
        result_b11=0
    #######################################
    # Filter Hydro Water Reservoir
    #######################################
    try:
        filter_b12 = jq.compile('.GL_MarketDocument.TimeSeries[] | select(.MktPSRType.psrType == "B12") | .Period.Point[0].quantity')
        result_b12 = filter_b12.input(data_dict).first()
    except:
        result_b12=0
    #######################################
    # Filter Nuclear
    #######################################
    try:
        filter_b14 = jq.compile('.GL_MarketDocument.TimeSeries[] | select(.MktPSRType.psrType == "B14") | .Period.Point[0].quantity')
        result_b14 = filter_b14.input(data_dict).first()
    except:
        result_b14=0
    #######################################
    # Filter Solar
    #######################################
    try:
        filter_b16 = jq.compile('.GL_MarketDocument.TimeSeries[] | select(.MktPSRType.psrType == "B16") | .Period.Point[0].quantity')
        result_b16 = filter_b16.input(data_dict).first()
    except:
        result_b16=0
    #######################################
    # Filter Waste
    #######################################
    try:
        filter_b17 = jq.compile('.GL_MarketDocument.TimeSeries[] | select(.MktPSRType.psrType == "B17") | .Period.Point[0].quantity')
        result_b17 = filter_b17.input(data_dict).first()
    except:
        result_b17=0
    #######################################
    # Filter Wind Offshore
    #######################################
    try:
        filter_b18 = jq.compile('.GL_MarketDocument.TimeSeries[] | select(.MktPSRType.psrType == "B18") | .Period.Point[0].quantity')
        result_b18 = filter_b18.input(data_dict).first()
    except:
        result_b18=0
    #######################################
    # Filter Wind Onshore
    #######################################
    try:
        filter_b19 = jq.compile('.GL_MarketDocument.TimeSeries[] | select(.MktPSRType.psrType == "B19") | .Period.Point[0].quantity')
        result_b19 = filter_b19.input(data_dict).first()
    except:
        result_b19=0
    #######################################
    # Factor CO2g/kWh
    #######################################
    fac_b01 = 230
    fac_b02 = 996
    fac_b05 = 880
    fac_b04 = 378
    fac_b09 = 91
    fac_b14 = 39
    fac_b19 = 9
    fac_b18 = 4
    fac_b16 = 26
    fac_b17 = 494
    fac_b10 = 23
    fac_b11 = 23
    fac_b12 = 23
    #######################################
    # Summary Energy Generation
    #######################################
    result_sum = int(result_b01) + int(result_b02) + int(result_b04) + int(result_b05) + int(result_b09) + int(result_b10) + int(result_b11) + int(result_b12) + int(result_b14) + int(result_b16) + int(result_b17) + int(result_b18) + int(result_b19)
    #######################################
    # Bio efficience
    #######################################
    if result_sum:
        result_eco = (int(result_b01) + int(result_b09) + int(result_b10) + int(result_b11) + int(result_b12) + int(result_b16) + int(result_b17) + int(result_b18) + int(result_b19)) / int(result_sum)
    else:
        result_eco = 0.99
    #######################################
    # Fossil part
    #######################################
    if result_sum:
        result_fos = (int(result_b02) + int(result_b04) + int(result_b05)) / int(result_sum)
    else:
        result_fos = 0.01
    #######################################
    # CO2 gramm/watt second
    #######################################
    result_co2 = ((int(result_b02) * (fac_b02 / 3600) / 1000 / 1000) + (int(result_b04) * (fac_b04 / 3600) / 1000 / 1000) + (int(result_b05) * (fac_b05 / 3600) / 1000 / 1000) + (int(result_b01) * (fac_b01 / 3600) / 1000 / 1000) + (int(result_b09) * (fac_b09/ 3600) / 1000 / 1000) + (int(result_b10) * (fac_b10 / 3600) / 1000 / 1000) + (int(result_b11) * (fac_b11 / 3600) / 1000 / 1000) + (int(result_b12) * (fac_b12 / 3600) / 1000 / 1000) + (int(result_b16) * (fac_b16 / 3600) / 1000 / 1000) + (int(result_b17) * (fac_b17 / 3600) / 1000 / 1000) + (int(result_b18) * (fac_b18 / 3600) / 1000 / 1000)  + (int(result_b19) * (fac_b19 / 3600) / 1000 / 1000))
    #######################################
    # Print Out Metrics
    #######################################
    counter = "# HELP entsoe_factor_b01 Factor CO2g/kWh Biomass" + "\n"
    counter += "# TYPE entsoe_factor_b01 gauge" + "\n"
    counter += "entsoe_factor_b01 " + str(fac_b01) + "\n"
    counter += "# HELP entsoe_factor_b02 Factor CO2g/kWh Brown Coal" + "\n"
    counter += "# TYPE entsoe_factor_b02 gauge" + "\n"
    counter += "entsoe_factor_b02 " + str(fac_b02) + "\n"
    counter += "# HELP entsoe_factor_b04 Factor CO2g/kWh Gas" + "\n"
    counter += "# TYPE entsoe_factor_b04 gauge" + "\n"
    counter += "entsoe_factor_b04 " + str(fac_b04) + "\n"
    counter += "# HELP entsoe_factor_b05 Factor CO2g/kWh Hard Coal" + "\n"
    counter += "# TYPE entsoe_factor_b05 gauge" + "\n"
    counter += "entsoe_factor_b05 " + str(fac_b05) + "\n"
    counter += "# HELP entsoe_factor_b10 Factor CO2g/kWh Hydro Pumped Storage" + "\n"
    counter += "# TYPE entsoe_factor_b10 gauge" + "\n"
    counter += "entsoe_factor_b10 " + str(fac_b10) + "\n"
    counter += "# HELP entsoe_factor_b11 Factor CO2g/kWh Hydro Run River" + "\n"
    counter += "# TYPE entsoe_factor_b11 gauge" + "\n"
    counter += "entsoe_factor_b11 " + str(fac_b11) + "\n"
    counter += "# HELP entsoe_factor_b12 Factor CO2g/kWh Hydro Water Reservoir" + "\n"
    counter += "# TYPE entsoe_factor_b12 gauge" + "\n"
    counter += "entsoe_factor_b12 " + str(fac_b12) + "\n"
    counter += "# HELP entsoe_factor_b14 Factor CO2g/kWh Nuclear" + "\n"
    counter += "# TYPE entsoe_factor_b14 gauge" + "\n"
    counter += "entsoe_factor_b14 " + str(fac_b14) + "\n"
    counter += "# HELP entsoe_factor_b16 Factor CO2g/kWh Solar" + "\n"
    counter += "# TYPE entsoe_factor_b16 gauge" + "\n"
    counter += "entsoe_factor_b16 " + str(fac_b16) + "\n"
    counter += "# HELP entsoe_factor_b17 Factor CO2g/kWh Waste" + "\n"
    counter += "# TYPE entsoe_factor_b17 gauge" + "\n"
    counter += "entsoe_factor_b17 " + str(fac_b17) + "\n"
    counter += "# HELP entsoe_factor_b18 Factor CO2g/kWh Wind Offshore" + "\n"
    counter += "# TYPE entsoe_factor_b18 gauge" + "\n"
    counter += "entsoe_factor_b18 " + str(fac_b18) + "\n"
    counter += "# HELP entsoe_factor_b19 Factor CO2g/kWh Wind Onshore" + "\n"
    counter += "# TYPE entsoe_factor_b19 gauge" + "\n"
    counter += "entsoe_factor_b19 " + str(fac_b19) + "\n"
    counter += "# HELP entsoe_generation_b01 Current generation of energy with Biomass in MW" + "\n"
    counter += "# TYPE entsoe_generation_b01 gauge" + "\n"
    counter += "entsoe_generation_b01 " + str(result_b01) + "\n"
    counter += "# HELP entsoe_generation_b02 Current generation of energy with Fossil Brown coal/Lignite in MW" + "\n"
    counter += "# TYPE entsoe_generation_b02 gauge" + "\n"
    counter += "entsoe_generation_b02 " + str(result_b02) + "\n"
    counter += "# HELP entsoe_generation_b04 Current generation of energy with Fossil Gas in MW" + "\n"
    counter += "# TYPE entsoe_generation_b04 gauge" + "\n"
    counter += "entsoe_generation_b04 " + str(result_b04) + "\n"
    counter += "# HELP entsoe_generation_b05 Current generation of energy with Fossil Hard coal in MW" + "\n"
    counter += "# TYPE entsoe_generation_b05 gauge" + "\n"
    counter += "entsoe_generation_b05 " + str(result_b05) + "\n"
    counter += "# HELP entsoe_generation_b09 Current generation of energy with Geothermal in MW" + "\n"
    counter += "# TYPE entsoe_generation_b09 gauge" + "\n"
    counter += "entsoe_generation_b09 " + str(result_b09) + "\n"
    counter += "# HELP entsoe_generation_b10 Current generation of energy with Hydro Pumped Storage in MW" + "\n"
    counter += "# TYPE entsoe_generation_b10 gauge" + "\n"
    counter += "entsoe_generation_b10 " + str(result_b10) + "\n"
    counter += "# HELP entsoe_generation_b11 Current generation of energy with Hydro Run-of-river and poundage in MW" + "\n"
    counter += "# TYPE entsoe_generation_b11 gauge" + "\n"
    counter += "entsoe_generation_b11 " + str(result_b11) + "\n"
    counter += "# HELP entsoe_generation_b12 Current generation of energy with Hydro Water Reservoir in MW" + "\n"
    counter += "# TYPE entsoe_generation_b12 gauge" + "\n"
    counter += "entsoe_generation_b12 " + str(result_b12) + "\n"
    counter += "# HELP entsoe_generation_b14 Current generation of energy with Nuclear in MW" + "\n"
    counter += "# TYPE entsoe_generation_b14 gauge" + "\n"
    counter += "entsoe_generation_b14 " + str(result_b14) + "\n"
    counter += "# HELP entsoe_generation_b16 Current generation of energy with Solar in MW" + "\n"
    counter += "# TYPE entsoe_generation_b16 gauge" + "\n"
    counter += "entsoe_generation_b16 " + str(result_b16) + "\n"
    counter += "# HELP entsoe_generation_b17 Current generation of energy with Waste in MW" + "\n"
    counter += "# TYPE entsoe_generation_b17 gauge" + "\n"
    counter += "entsoe_generation_b17 " + str(result_b17) + "\n"
    counter += "# HELP entsoe_generation_b18 Current generation of energy with Wind Offshore in MW" + "\n"
    counter += "# TYPE entsoe_generation_b18 gauge" + "\n"
    counter += "entsoe_generation_b18 " + str(result_b18) + "\n"
    counter += "# HELP entsoe_generation_b19 Current generation of energy with Wind Onshore in MW" + "\n"
    counter += "# TYPE entsoe_generation_b19 gauge" + "\n"
    counter += "entsoe_generation_b19 " + str(result_b19) + "\n"
    counter += "# HELP entsoe_generation_sum Current generation of energy summary in MW" + "\n"
    counter += "# TYPE entsoe_generation_sum gauge" + "\n"
    counter += "entsoe_generation_sum " + str(result_sum) + "\n"
    counter += "# HELP entsoe_generation_eco Current generation of eco energy summary rate" + "\n"
    counter += "# TYPE entsoe_generation_eco gauge" + "\n"
    counter += "entsoe_generation_eco " + str(result_eco) + "\n"
    counter += "# HELP entsoe_generation_fos Current generation of fossil energy summary rate" + "\n"
    counter += "# TYPE entsoe_generation_fos gauge" + "\n"
    counter += "entsoe_generation_fos " + str(result_fos) + "\n"
    counter += "# HELP entsoe_generation_co2 Current generation of co2 per watt per second" + "\n"
    counter += "# TYPE entsoe_generation_co2 gauge" + "\n"
    counter += "entsoe_generation_co2 " + str(result_co2) + "\n"
    
    #######################################
    #json_data = json.dumps(data_dict)
    #print(json_data,file=open('data.json','w'))

    return counter, 200, {'Content-Type': 'text/plain'}

@app.errorhandler(404)
def not_found_error(error):
    message = "Couldn't found your requested page"
    return message, 404, {'Content-Type': 'text/plain'}

@app.errorhandler(500)
def internal_error(error):
    message = "Something went wrong"
    return message, 500, {'Content-Type': 'text/plain'}

if __name__ == '__main__':

  app.run(
    host = "0.0.0.0",
    port = 9091,
    debug = 0
  )
