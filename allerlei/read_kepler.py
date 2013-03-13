import pandas as pd
from pandas import Series, DataFrame

def read_kepler(file):
    """
    """
    # 1st two lines in the file constitutes metadata.  Ignore for now.

    # Search for the lines with 'Quarter'.  Keep track of these line numbers
    quarters = []
    for (idx, line) in enumerate(open(file)):
        if line.startswith('Quarter'):
            quarters.append(idx)


    # We have the line numbers that tell where a quarter starts.  The starting
    # point of the next quarter tells us how many lines to read.  We can fake
    # out that last quarter by appending the last line number of the file + 1.
    quarters.append(idx+1)
    frames = []
    for j in range(len(quarters)-1):
        skiprows = quarters[j]
        nrows = quarters[j+1] - skiprows - 1

        df = pd.read_csv(file, skiprows=skiprows, nrows=nrows)

        # Drop any rows with NaNs
        df = df.dropna()
        frames.append(df)

    return(frames)

if __name__ == "__main__":
    frames = read_kepler('/opt/data/astronomy/SPH10045630.csv')
    print(len(frames))

