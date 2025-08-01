
from gmx_python_sdk.scripts.v2.get.get_funding_apr import GetFundingFee
from gmx_python_sdk.scripts.v2.get.get_borrow_apr import GetBorrowAPR

from gmx_python_sdk.scripts.v2.gmx_utils import ConfigManager

import pandas as pd

from synthetix import Synthetix


"""
    To use the library, initialize the Synthetix object that can be used to interact with the protocol. At minimum, you must provide an RPC endpoint.
"""
snx = Synthetix(
    provider_rpc="https://base-mainnet.infura.io/v3/a9989a4510d34af9971289e6906ed492",
)
"""
    This creates an snx object that helps you interact with the protocol smart contracts. At minimum you need to provide the provider_url parameter, which is the RPC endpoint of the node you want to connect to. If there are any warnings or errors during initialization, they are logged to the console.
"""
def create_funding_dataframe(gmx_funding_rate_data, gmx_borrowing_rate_data, synthetix_data):
    """
    Converts fetched funding data into a pandas DataFrame.
    """
    gmx_df1 = pd.DataFrame(
        gmx_funding_rate_data
    ).drop(
        columns=["parameter"]
    )
    gmx_df1 = gmx_df1.reset_index().rename(
        columns={'index': 'Coin', 'long': 'Long Funding APR', 'short': 'Short Funding APR'}
    )
    # Remove rows where 'Long Funding APR' is 0loc
    gmx_df1 = gmx_df1[~((gmx_df1["Long Funding APR"] == 0) & (gmx_df1["Short Funding APR"] == 0))]
    # gmx_df1.iloc[:, 1:] = gmx_df1.iloc[:, 1:].apply(lambda x: f"{x * 100:.2f}%")

    gmx_df1["Long Funding APR"] = gmx_df1["Long Funding APR"] * 100
    gmx_df1["Short Funding APR"] = gmx_df1["Short Funding APR"] * 100

    gmx_df2 = pd.DataFrame(
        gmx_borrowing_rate_data
    ).drop(
        columns=["parameter"]
    )
    gmx_df2 = gmx_df2.reset_index().rename(
        columns={'index': 'Coin', 'long': 'Long Funding APR', 'short': 'Short Funding APR'}
    )
    # Remove rows where 'Long Funding APR' is 0loc
    gmx_df2 = gmx_df2[~((gmx_df2["Long Funding APR"] == 0) & (gmx_df2["Short Funding APR"] == 0))]
    # gmx_df2.iloc[:, 1:] = gmx_df2.iloc[:, 1:].apply(lambda x: f"{x * 100:.2f}%")

    gmx_df2["Long Funding APR"] = gmx_df2["Long Funding APR"] * 100
    gmx_df2["Short Funding APR"] = gmx_df2["Short Funding APR"] * 100

    gmx_df = pd.merge(
        gmx_df1[['Coin', 'Long Funding APR', 'Short Funding APR']],
        gmx_df2[['Coin', 'Long Funding APR', 'Short Funding APR']],
        on='Coin',
        how='outer',
        suffixes=('_funding', '_borrow')
    )
    print("==============================================")
    print(gmx_df)
    print("==============================================")
    gmx_df['Long Funding APR'] = (
        gmx_df['Long Funding APR_funding'].fillna(0) +
        gmx_df['Long Funding APR_borrow'].fillna(0)
    )
    gmx_df['Short Funding APR'] = (
        gmx_df['Short Funding APR_funding'].fillna(0) +
        gmx_df['Short Funding APR_borrow'].fillna(0)
    )
    gmx_df = gmx_df[['Coin', 'Long Funding APR', 'Short Funding APR']]
    print("==============================================result gmx df=========================================")
    print(gmx_df)
    print("==============================================")
    gmx_df = gmx_df[~((gmx_df['Long Funding APR'] == 0) & 
                               (gmx_df['Short Funding APR'] == 0))]

    synthetix_filtered_data = [(value['market_name'], value['current_funding_rate']) for value in synthetix_data.values()]
    synthetix_df = pd.DataFrame(
        synthetix_filtered_data, columns=['Market Name', 'Current Funding Rate']
    )
    synthetix_df["Annualized Funding Rate"] = synthetix_df["Current Funding Rate"] * 8760
    # synthetix_df["1H Funding Rate"] = synthetix_df["Current Funding Rate"]
    synthetix_df = synthetix_df.drop(columns=["Current Funding Rate"])

    return gmx_df, synthetix_df

def main():
    to_json = False
    to_csv = False

    config = ConfigManager(chain='arbitrum')
    config.set_config("./config.yaml")

    stats_object = GetGMXv2Stats(
        config=config,
        to_json=to_json,
        to_csv=to_csv
    )

    """
    Main function to fetch and display funding data from GMX and Synthetix.
    """
    print("Fetching GMX funding data...")
    gmx_funding_rate_data = stats_object.get_funding_apr()
    gmx_borrow_rate_data = stats_object.get_borrowing_apr()

    
    print("\nFetching Synthetix funding data...")
    synthetix_data, _ = snx.perps.get_markets()
    
    # Create DataFrames
    gmx_df, synthetix_df = create_funding_dataframe(gmx_funding_rate_data, gmx_borrow_rate_data, synthetix_data)
    
    return gmx_df, synthetix_df
    # create_funding_dataframe(gmx_funding_rate_data, gmx_borrow_rate_data, synthetix_data)

class GetGMXv2Stats:

    def __init__(self, config, to_json, to_csv):
        self.config = config
        self.to_json = to_json
        self.to_csv = to_csv

    def get_funding_apr(self):

        return GetFundingFee(
            self.config
        ).get_data(
            to_csv=self.to_csv,
            to_json=self.to_json
        )
    def get_borrowing_apr(self):
        return GetBorrowAPR(
            self.config
        ).get_data(
            to_csv=self.to_csv,
            to_json=self.to_json
        )

if __name__ == "__main__":
    
    # main()
    gmx_df, synthetix_df = main()

    print("\nGMX Funding Data:")
    print(gmx_df)
    gmx_df.to_json("gmx_funding_data.json", orient='records', indent=4)
    print("\ngmx_funding_data.json file created.")
    
    print("\nSynthetix Funding Data:")
    print(synthetix_df)
    synthetix_df.to_json("synthetix_funding_data.json", orient='records', indent=4)
    print("\nsynthetix_funding_data.json file created.")


"""
    Installing Environment:
        $ pip install pandas
        $ pip install gmx-python-sdk
        $ pip install Synthetix
    You should create config.yaml file in the venv/lib/python3.12/site-packages
        This creates an snx object that helps you interact with the protocol smart contracts. At minimum you need to provide the provider_url parameter, which is the RPC endpoint of the node you want to connect to. If there are any warnings or errors during initialization, they are logged to the console.
"""