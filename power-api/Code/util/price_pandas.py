import pandas

csv_file = "../data/price_generated.csv"

def price_comp():
    df = pandas.read_csv(csv_file)
    print(df.dtypes)

if __name__ == "__main__":
    price_comp()