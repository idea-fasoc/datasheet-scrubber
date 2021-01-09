import csv
import pandas as pd
import re
import json 
from pymongo import MongoClient
import glob

client = MongoClient()
#specify the name of the database
db=client.config
#specify the name of the collection, here my collection is "clean_test"
Digikey_py = db.clean_test

#Specify output from table extraction
#TODO: Search for files starting with concatenate
directory = '/Users/zinebbenameur/clean/datasheet-scrubber/concatenate_table*.csv'


#Read CSV files
i = 0

#list of fields to include in the filtered CSV file
list_to_search = 'Model|Battery|Delay|Time|Propagation|Drivers|Receivers|Display|Resistance|Wiper|Bits|Noise|Voltage|Supply|Dual (V±)|Spec|Resistance|Temperature|Memory Type|Full Scale|Voltage|Output (Max)|Size / Dimension|Number of LABs/CLBs|Configuration|Total RAM Bits|Number of|Circuits|Regulators|Gates|Format|Current|Modulation|fclk|Voltage|Input|Voltage|Output|Interrupt Output|Security Features|Voltage/Current|Output 1|Power (Watts)|Frequency|Max|Divider/Multiplier|With Modem Control|Voltage|I/O High|category|CMRR| PSRR (Typ)|Current|Input Bias|Standards|Sensor Type|FPGA Gates|Direction|Voltage|Load|Charge Current|Max|Max Output Power x Channels @ Load|Step Resolution|Duty Cycle|Speed|S/N Ratio|ADC|DAC|Co|Processors|DSP|Mode|Synchronous Rectifier|Controller Series|Capacity|3db Bandwidth|Clock Sync|Bus Directional|instance_name|Timing|Primary Attributes|Voltage|Supply| Single/Dual (±)|Current|Supply (Max)|INL/DNL (LSB)|Voltage|Start Up|USB|Battery Pack Voltage|Switch Time (Ton| Toff) (Max)|Voltage|Threshold|Number of Elements|Current|Quiescent (Iq)|On|Chip RAM|Voltage|Supply| Battery|Motor Type|AC| DC|Current|Output|Reset|Program Memory Type|Serial Interfaces|PSRR|Output Phases|Circuit|Channel Type|Supply Voltage|Programmable Flags Support|Output Type|Data SRAM Bytes|Voltage/Current|Output 3|Programmable Features|Current|Output High| Low|Voltage|I/O|Control Features|Messaging|FIFO|Connector Type|Amplifier Type|Number of I/O|Ratio|S/H:ADC|Memory Interface|Voltage|Supply (Max)|Sampling Frequency|Channel Capacitance (CS(off)| CD(off))|Power|Max|Filter Order|With False Start Bit Detection|Sigma Delta|Voltage|VCCB|Display & Interface Controllers|Current|Output (Typ)|Voltage|VCCA|Temperature Coefficient (Typ)|Non|Volatile Memory|Settling Time|Channel|to|Channel Matching (&Delta;Ron)|Digits or Characters|Connectivity|FPGA Core Cells|Voltage|Rated|Current|Timekeeping (Max)|Reference Type|Independent Circuits|Number of Drivers|Reset Timeout|Fault Protection|module_name|Current|Quiescent (Max)|Output Configuration|Number of Voltages Monitored|Voltage|Supply| Single (V+)|Input Signal|Output Isolation|Dynamic Range| ADCs / DACs (db) Typ|Category|Temperature Coefficient|Hysteresis|Propagation Delay|Logic Type|Voltage|Supply|Number of A/D Converters|Rise / Fall Time (Typ)|Voltage|Supply (Vcc/Vdd)|Delay Time|Graphics Acceleration|Access Time|Frequency|Number of D/A Converters|Current|Cathode|PLL|Logic Level|High|Voltage|Output (Min/Fixed)|Tap Increment|Interface|Delay Time|OFF|Touchscreen|Number of Terminations|Multiplexer/Demultiplexer Circuit|Rds On (Typ)|Number of Logic Elements/Blocks|Ethernet|Memory Size|Number of Taps|Clock Rate|w/LED Driver|Sampling Rate (Per Second)|Number of Bits|Logic Level|Low|Tolerance|Logic Voltage|VIL| VIH|Trigger Type|Accuracy|RAM Size|Voltage|Supply (Min)|Ratio|Input:Output|Type|High Side Voltage|Max (Bootstrap)|Count Rate|Taper|Delay to 1st Tap|Program SRAM Bytes|Voltage|Input (Min)|Technology|Voltage|Breakdown|Current|Leakage (IS(off)) (Max)|Co|Processor|FWFT Support|Current|Output (Max)|Digi|Key Part Number|Voltage|Input|Available Total Delays|Voltage|Input Offset|Memory Format|Flash Size|Number of Filters|Current|Output Source/Sink|Internal Switch(s)|Input Type|FPGA Registers|Translator Type|Charge Injection|EEPROM Size|Duplex|Channels per Circuit|Current|Input Bias (Max)|Voltage Supply Source|Core Processor|Input Impedance|Operating Temperature|Datasheets|Voltage Dropout (Max)|Capacitance|Input|Expansion Type|SATA|Topology|Current|Supply|RAM Controllers|Delay Time|ON|Tuning Word Width (Bits)|Retransmit Capability|With Auto Flow Control|Voltage|Input (Max)|LED Driver Channels|Applications|On|State Resistance (Max)|Duration|Core Type|Current|Startup|Switch Type|Filter Type|Switch Circuit|Auxiliary Sense|Current|Peak Output|Frequency|Switching|Differential|Input:Output|Delay Time tpd(1) Max|Output|Features|Schmitt Trigger Input|Current|Bias|Voltage/Current|Output 2|Data Interface|Proximity Detection|Motor Type|Stepper|Propagation Delay (Max)|Number of Independent Delays|w/Supervisor|Output Alarm|Image|Current|Output / Channel|Baud Rates|Meter Type|Function|Mounting Type|Duty Cycle (Max)|Filter Pass Band|Date Format|Programmable Type|Receiver Hysteresis|Output Fan|FPGA SRAM|Manufacturer|Write Cycle Time|Word| Page|Count|Data Format|Current|Peak Output (Source| Sink)|Input Capacitance|Supplier Device Package|Module/Board Type|Number of Cells|Data Rate|Protocol|Output Signal|Main Purpose|Series|Gate Type|Load Capacitance|Current|Charging|w/Sequencer|Peripherals|Architecture|Load Type|specifications|Voltage|Core|Linearity|Noise|0|1Hz to 10Hz|Frequency|Cutoff or Center|Number of Outputs|Manufacturer Part Number|Part Status|Number of Bits/Stages|Data Converters|Input|Number of ADCs / DACs|Sensing Method|Sensing Temperature|Driven Configuration|FET Type|Core Size|Voltage Supply|Internal|Description|Number of Logic Elements/Cells|With IrDA Encoder/Decoder|Subcategory|Oscillator Type|Controller Type|Number of Taps/Steps|Gain Bandwidth Product|Voltage|Supply| Analog|Notification|Number of Cores/Bus Width|Slew Rate|Number of Channels|Crosstalk|Number of Macrocells|Dimming|Voltage Reference|Resolution|Output Function|Measurement Error|Program Memory Size|Package / Case|Data Rate (Max)|Protection Features|Number of Inputs|Signal|Conditioning|Resolution|Differential|Voltage|Supply|Digital|Clock|Frequency'


for filename in glob.glob(directory):
    print("------------", filename , "------------------")
    i = i+1
    cols = pd.read_csv(filename, nrows =1)
    cols_to_use = [i for i in cols.columns if re.search(list_to_search,i, re.IGNORECASE)] 

    #create new dataframe
    df=pd.read_csv(filename,header=0, skiprows=0, skipfooter=0, usecols  =cols_to_use)
    print("cleaned df", df)
    df.columns = df.columns.str.replace("[.]", ",")
    #Copy dataframe to csv file
    #new_file=df.to_csv("cleanCSV"+str(i)+".csv", index=False)
    
    #df_new = pd.read_csv("cleanCSV"+str(i)+".csv")
    #print("cleaned df", df)

    #Copy Dataframe to json (for easier insertion)
    #df.to_json("test.json", orient='records')
    if not df.empty:
        Digikey_py.insert_many(df.to_dict('records'))
    else:
        continue
#TODO Insert CSV in DB

print("----- TOTAL NUMBER OF CSV inserted and inserted------",i)
