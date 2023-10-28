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
    client = EntsoeRawClient(api_key=entsoe_api_key)
    # Compute the time window from yesterday within 1 hour
    today = datetime.today()
    TwentyFour = (today - timedelta(hours = int(entsoe_end) ))
    TwentyFive = (today - timedelta(hours = int(entsoe_start) ))
    start = pd.Timestamp(TwentyFive, tz='Europe/Berlin')
    end = pd.Timestamp(TwentyFour, tz='Europe/Berlin')
    # Relates country is Germany
    country_code = 'DE'
    
    # Query all energy generation in this time window for this country
    try:
        df_generation = client.query_generation(country_code, start=start,end=end, nett=True)
        data_dict = xmltodict.parse(df_generation)
    except:
        message = "No data from API"
        return message, 500, {'Content-Type': 'text/plain'}
    
    #######################################
    # Filter Biomass
    # ref: https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html#_psrtype
    try:
        filter_b01 = jq.compile('.GL_MarketDocument.TimeSeries[] | select(.MktPSRType.psrType == "B01") | .Period.Point[0].quantity')
        result_b01 = filter_b01.input(data_dict).first()
    except:
        result_b01=0
    #######################################
    # Filter Fossil Brown coal/Lignite
    try:
        filter_b02 = jq.compile('.GL_MarketDocument.TimeSeries[] | select(.MktPSRType.psrType == "B02") | .Period.Point[0].quantity')
        result_b02 = filter_b02.input(data_dict).first()
    except:
        result_b02=0
    #######################################
    # Filter Fossil Gas
    try:
        filter_b04 = jq.compile('.GL_MarketDocument.TimeSeries[] | select(.MktPSRType.psrType == "B04") | .Period.Point[0].quantity')
        result_b04 = filter_b04.input(data_dict).first()
    except:
        result_b04=0
    #######################################
    # Filter Fossil Hard coal
    try:
        filter_b05 = jq.compile('.GL_MarketDocument.TimeSeries[] | select(.MktPSRType.psrType == "B05") | .Period.Point[0].quantity')
        result_b05 = filter_b05.input(data_dict).first()
    except:
        result_b05=0
    #######################################
    # Filter Geothermal
    try:
        filter_b09 = jq.compile('.GL_MarketDocument.TimeSeries[] | select(.MktPSRType.psrType == "B09") | .Period.Point[0].quantity')
        result_b09 = filter_b09.input(data_dict).first()
    except:
        result_b09=0
    #######################################
    # Filter Hydro Pumped Storage
    try:
        filter_b10 = jq.compile('.GL_MarketDocument.TimeSeries[] | select(.MktPSRType.psrType == "B10") | .Period.Point[0].quantity')
        result_b10 = filter_b10.input(data_dict).first()
    except:
        result_b10=0
    #######################################
    # Filter Hydro Run-over-river and poundage
    try:
        filter_b11 = jq.compile('.GL_MarketDocument.TimeSeries[] | select(.MktPSRType.psrType == "B11") | .Period.Point[0].quantity')
        result_b11 = filter_b11.input(data_dict).first()
    except:
        result_b11=0
    #######################################
    # Filter Hydro Water Reservoir
    try:
        filter_b12 = jq.compile('.GL_MarketDocument.TimeSeries[] | select(.MktPSRType.psrType == "B12") | .Period.Point[0].quantity')
        result_b12 = filter_b12.input(data_dict).first()
    except:
        result_b12=0
    #######################################
    # Filter Nuclear
    try:
        filter_b14 = jq.compile('.GL_MarketDocument.TimeSeries[] | select(.MktPSRType.psrType == "B14") | .Period.Point[0].quantity')
        result_b14 = filter_b14.input(data_dict).first()
    except:
        result_b14=0
    #######################################
    # Filter Solar
    try:
        filter_b16 = jq.compile('.GL_MarketDocument.TimeSeries[] | select(.MktPSRType.psrType == "B16") | .Period.Point[0].quantity')
        result_b16 = filter_b16.input(data_dict).first()
    except:
        result_b16=0
    #######################################
    # Filter Waste
    try:
        filter_b17 = jq.compile('.GL_MarketDocument.TimeSeries[] | select(.MktPSRType.psrType == "B17") | .Period.Point[0].quantity')
        result_b17 = filter_b17.input(data_dict).first()
    except:
        result_b17=0
    #######################################
    # Filter Wind Offshore
    try:
        filter_b18 = jq.compile('.GL_MarketDocument.TimeSeries[] | select(.MktPSRType.psrType == "B18") | .Period.Point[0].quantity')
        result_b18 = filter_b18.input(data_dict).first()
    except:
        result_b18=0
    #######################################
    # Filter Wind Onshore
    try:
        filter_b19 = jq.compile('.GL_MarketDocument.TimeSeries[] | select(.MktPSRType.psrType == "B19") | .Period.Point[0].quantity')
        result_b19 = filter_b19.input(data_dict).first()
    except:
        result_b19=0
    #######################################
    # Summary Energy Generation
    result_sum = int(result_b01) + int(result_b02) + int(result_b04) + int(result_b04) + int(result_b09) + int(result_b10) + int(result_b11) + int(result_b12) + int(result_b14) + int(result_b16) + int(result_b18) + int(result_b18) + int(result_b19)
    
    # Print Out Metrics
    counter = "# HELP entsoe_generation_b01 Current generation of energy with Biomass in MW" + "\n"
    counter += "# TYPE entsoe_generation_b01 counter" + "\n"
    counter += "entsoe_generation_b01 " + str(result_b01) + "\n"
    counter += "# HELP entsoe_generation_b02 Current generation of energy with Fossil Brown coal/Lignite in MW" + "\n"
    counter += "# TYPE entsoe_generation_b02 counter" + "\n"
    counter += "entsoe_generation_b02 " + str(result_b02) + "\n"
    counter += "# HELP entsoe_generation_b04 Current generation of energy with Fossil Gas in MW" + "\n"
    counter += "# TYPE entsoe_generation_b04 counter" + "\n"
    counter += "entsoe_generation_b04 " + str(result_b04) + "\n"
    counter += "# HELP entsoe_generation_b05 Current generation of energy with Fossil Hard coal in MW" + "\n"
    counter += "# TYPE entsoe_generation_b05 counter" + "\n"
    counter += "entsoe_generation_b05 " + str(result_b05) + "\n"
    counter += "# HELP entsoe_generation_b09 Current generation of energy with Geothermal in MW" + "\n"
    counter += "# TYPE entsoe_generation_b09 counter" + "\n"
    counter += "entsoe_generation_b09 " + str(result_b09) + "\n"
    counter += "# HELP entsoe_generation_b10 Current generation of energy with Hydro Pumped Storage in MW" + "\n"
    counter += "# TYPE entsoe_generation_b10 counter" + "\n"
    counter += "entsoe_generation_b10 " + str(result_b10) + "\n"
    counter += "# HELP entsoe_generation_b11 Current generation of energy with Hydro Run-of-river and poundage in MW" + "\n"
    counter += "# TYPE entsoe_generation_b11 counter" + "\n"
    counter += "entsoe_generation_b11 " + str(result_b11) + "\n"
    counter += "# HELP entsoe_generation_b12 Current generation of energy with Hydro Water Reservoir in MW" + "\n"
    counter += "# TYPE entsoe_generation_b12 counter" + "\n"
    counter += "entsoe_generation_b12 " + str(result_b12) + "\n"
    counter += "# HELP entsoe_generation_b14 Current generation of energy with Nuclear in MW" + "\n"
    counter += "# TYPE entsoe_generation_b14 counter" + "\n"
    counter += "entsoe_generation_b14 " + str(result_b14) + "\n"
    counter += "# HELP entsoe_generation_b16 Current generation of energy with Solar in MW" + "\n"
    counter += "# TYPE entsoe_generation_b16 counter" + "\n"
    counter += "entsoe_generation_b16 " + str(result_b16) + "\n"
    counter += "# HELP entsoe_generation_b17 Current generation of energy with Waste in MW" + "\n"
    counter += "# TYPE entsoe_generation_b17 counter" + "\n"
    counter += "entsoe_generation_b17 " + str(result_b17) + "\n"
    counter += "# HELP entsoe_generation_b18 Current generation of energy with Wind Offshore in MW" + "\n"
    counter += "# TYPE entsoe_generation_b18 counter" + "\n"
    counter += "entsoe_generation_b18 " + str(result_b18) + "\n"
    counter += "# HELP entsoe_generation_b19 Current generation of energy with Wind Onshore in MW" + "\n"
    counter += "# TYPE entsoe_generation_b19 counter" + "\n"
    counter += "entsoe_generation_b19 " + str(result_b19) + "\n"
    counter += "# HELP entsoe_generation_sum Current generation of energy summary in MW" + "\n"
    counter += "# TYPE entsoe_generation_sum counter" + "\n"
    counter += "entsoe_generation_sum " + str(result_sum) + "\n"
    
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
