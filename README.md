# Crypto Arbitrage Trading Project

## Required Libraries & Installation

This project requires the following libraries:

- **Python 3.6+**  
  Minimum required Python version.

- **ccxt**  
  For interacting with various cryptocurrency exchange APIs.  
  Install with: `pip install ccxt`

- **requests**  
  For making HTTP requests.  
  Install with: `pip install requests`

- **schedule**  
  For scheduling periodic tasks (e.g., price checks or trades).  
  Install with: `pip install schedule`

- **pandas**  
  For data manipulation and analysis.  
  Install with: `pip install pandas`

- **numpy**  
  For numerical computations and array operations.  
  Install with: `pip install numpy`

- **python-dotenv**  
  For managing sensitive data using a `.env` file.  
  Install with: `pip install python-dotenv`


Then, install all dependencies at once with:

```bash
pip install -r requirements.txt
```

## Setting Up Environment Variables

To use `os.getenv` in this project, create a file named `.env` in the project's root directory and add your API keys like so:

```env
BINANCE_API_KEY=your_actual_api_key_here
BINANCE_API_SECRET=your_actual_api_secret_here
```
