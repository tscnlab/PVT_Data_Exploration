import pandas as pd
import numpy as np
import glob

processedData = []
def preprocessData(filename=np.nan, maxThreshold_ms=500, minThreshold_ms=200):
    global processedData

    # Get a list of file paths that match the pattern in the 'filename' argument
    light_csv = glob.glob(filename, recursive=True)

    for file in light_csv:
        # Import file
        titles = [title for title in pd.read_csv(filename)]
        df = pd.read_csv(file, converters={"Keys pressed": lambda x: x.strip("[]").split(", "), 
                                          "Response Times": lambda x: x.strip("[]").split(", ")})
        
        # exploding the rows with two responses
        df = df.explode(["Keys pressed", "Response Times"])
        
        # Convert keypressed and response time to numeric
        df["Keys pressed"] = pd.to_numeric(df["Keys pressed"], downcast='integer') 
        df["Response Times"] = pd.to_numeric(df["Response Times"], downcast='integer') 

        # Convert string to datetime
        df['Timestamps_string'] = df[titles[0]]
        df[titles[0]] = pd.to_datetime(df[titles[0]])
        
        # Finding the false alarms
        RepRes = df.duplicated(subset=['Timestamps_string'])
        quickRes = df["Response Times"] <= minThreshold_ms 
        df['False alarms'] = (RepRes | quickRes).astype(int)
        
        # Determining misses, empty array and if the RT is greater than 500
        delayedRes = df["Response Times"] >= maxThreshold_ms 
        noRes = df["Keys pressed"].isnull()
        df['Misses'] = (delayedRes | noRes).astype(int)
        
        # Determine hits
        df['Hits'] = (~np.logical_or(df['False alarms'], df['Misses'])).astype(int)
        RTs = df.loc[df['Hits']==1,'Response Times']
        #print(RTs)
        processedData.append(df)
        
    #print(processedData)
    # Concatenate all data frames after the loop
    concatData = pd.concat(processedData, ignore_index=True)
    #print(concatData)
    return concatData

""" # Call the function
filename = "aPVT_darkCondition/*.csv"
df = preprocessData(filename) """

