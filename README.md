# Stock Market News Monitor

A Python-based real-time news monitoring system for stock market analysis.

## 📋 Description

This application monitors soy-related news in real-time using the NewsAPI service, helping traders and investors stay informed about potential price-moving events for their selected stocks.

## 🚀 Features

- Real-time News Monitoring: Track news for multiple stock tickers simultaneously
- Keyword Analysis: Automatic detection of price-moving keywords in news articles
- Flexible Configuration: Customizable refresh intervals and stock selections
- Logging System: Comprehensive logging of news alerts and system events

## ⚙️ Installation

1. **Clone the repository**
```bash
git clone https://github.com/HL0v/Desafio_itau_quant
cd DIQ
```

2. **Set up virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # For Linux/Mac
# or
.\venv\Scripts\activate  # For Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Install required packages**
```bash
pip install newsapi-python schedule pandas
```

5. **Configure API Key**
   - Get your API key from [NewsAPI](https://newsapi.org/)
   - Create a file named `apikeys.txt` and add your key
   - Or use the key directly with the `--api-key` parameter

## 💻 Usage

Run the monitor with your chosen stock tickers:

```bash
python backtest.py
```

### Parameters:
- `tickers`: One or more stock symbols (required)
- `--api-key`: Your NewsAPI key (required)
- `--interval`: News refresh interval in seconds (default: 60)

## 📁 Project Structure

```
stock-news-monitor/
├── backtest.py        # Main application script
├── requirements.txt   # Python dependencies
├── .gitignore        # Git ignore configuration
└── README.md         # Project documentation
```

## 🔒 Git Ignored Files

```
venv/               # Virtual environment
apikeys.txt         # API key storage
Quant_Expert/       # Expert system files
oldlogs.txt         # Historical logs
.vscode/           # VS Code settings
```

## 📝 Logs

The application generates two types of logs:
- `stock_monitor.log`: System events and errors
- `articles.log`: Detailed news article information

## Dependencies

Create a `requirements.txt` file with:

```txt
newsapi-python==0.2.7
schedule==1.2.0
pandas==2.0.3
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is for informational purposes only. Always verify news from multiple sources before making investment decisions.