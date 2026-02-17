# Company Research & Partner Sourcing Agent

An automated tool to find consulting firms, studios, and transformation boutiques that are partner-ready for SaaS, Cloud, AI/ML, QA, and white-label execution.

## Features

- 🔍 **Smart Search**: Uses Serper API for reliable, high-quality search results
- ✅ **Intelligent Validation**: Filters companies based on:
  - Partner/Ecosystem language
  - Consulting/strategy roles
  - Outcome-based positioning
  - Business transformation focus
- 📊 **Rich Output**: Generates markdown tables with company details and LinkedIn search strings
- 🎯 **Customizable**: Pre-configured high-intent queries for different consulting niches

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Serper API Key

1. Go to [serper.dev](https://serper.dev/)
2. Sign up for a free account
3. Get your API key from the dashboard
4. Free tier includes 2,500 searches/month

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your Serper API key:

```
SERP_API_KEY=your_actual_api_key_here
```

### 4. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage

1. **Select Queries**: Choose from pre-defined high-intent search queries
2. **Set Limit**: Adjust how many search results to fetch per query (more = slower but comprehensive)
3. **Run**: Click 'Start Research'
4. **Review**: The agent will search, validate, and present a shortlist of partner-ready companies
5. **Export**: Download results as CSV or Markdown

## Validation Criteria

Companies are accepted if they meet **any** of these criteria:

- ✅ Mention partner/ecosystem/implementation concepts
- ✅ Hiring for consulting/strategy roles
- ✅ Use outcome-based language (ROI, transformation, value)
- ✅ Position themselves as consulting/strategy firms

Companies are **rejected** if:

- ❌ Primarily staff augmentation/body shops
- ❌ Engineering roles vastly outnumber consulting roles without consulting positioning

## Project Structure

```
company-research-agent/
├── app.py                      # Streamlit UI
├── agent_logic.py              # Core search and validation logic
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this)
├── .env.example                # Environment variables template
├── test_validation_logic.py    # Unit tests for validation
└── README.md                   # This file
```

## Testing

Run unit tests:

```bash
python test_validation_logic.py
```

## Troubleshooting

### "SERP_API_KEY environment variable not set"

Make sure you:
1. Created a `.env` file in the project root
2. Added `SERP_API_KEY=your_key` to the file
3. Restarted the Streamlit app

### No results found

- Check your API key is valid
- Verify you haven't exceeded your monthly quota
- Try simpler search queries
- Check the Serper dashboard for API status

## License

MIT
