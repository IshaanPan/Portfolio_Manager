from yahoo_scraper import Data
from portfolio import Portfolio
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
data=Portfolio()
data.construct_portfolio()
data.load_data()
data.construct_tracker()
data.finalise_tracker()
data.plotting_tracker()


