# 404

A Streamlit application for **Yippie**, an energy company. This app is designed to help retain existing customers in their contracts and attract new customers through an engaging user experience.

## About

This application serves Yippie's customer engagement goals:
- **Customer Retention**: Keep existing customers engaged and satisfied with their energy contracts
- **Customer Acquisition**: Attract and invite new customers to join Yippie
- **Customer Intelligence**: Gather insights and data about customer behavior, preferences, and engagement patterns

The app provides features for challenges, rewards, and user management to enhance customer experience and loyalty.

## Setup

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

### Prerequisites

- Python 3.9 or higher
- [uv](https://github.com/astral-sh/uv) package manager

To install uv:
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via Homebrew
brew install uv
```

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd 404
```

2. Install dependencies using uv:
```bash
uv sync
```

This will:
- Create a virtual environment (`.venv/`)
- Install all project dependencies.

## Running the Application

### Streamlit Frontend

Run the Streamlit application:
```bash
uv run streamlit run frontend/main.py
```

The app will be available at `http://localhost:8501`

### Data Generation Script

Run the data generation script:
```bash
uv run python data-generation-scripts/dataGen.py
```

## Project Structure

```
404/
├── frontend/
│   ├── main.py              # Main Streamlit application
│   └── pages/               # Streamlit pages
│       ├── ChallengesPage.py
│       ├── RewardsPage.py
│       └── UserPages.py
├── data-generation-scripts/
│   └── dataGen.py           # Data generation using Google GenAI
├── pyproject.toml            # Project dependencies and configuration
└── README.md
```

## Dependencies

- **streamlit** (>=1.28.0) - Web application framework
- **google-genai** (>=0.2.0) - Google Generative AI client

All dependencies are managed through `uv` and defined in `pyproject.toml`.