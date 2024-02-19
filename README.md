# Synchaev

## Introduction

Synchaev is a user interface designed for interacting  with agent training data created using a synthetic (LLM created) environment.

## Features


To install Synchaev, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/synchaev.git
   ```
2. Navigate to the project directory
   ```bash
   cd synchaev
   ```
3. Install from source
   ```bash
   pip install -e .
   ```
   
## Usage
Launch the application with streamlit:
```bash
export OPENAI_API_KEY="sk-<your_key>"
streamlit run ./app.py
```

Record Agent-Environment conversation:
```bash
python ./record.py 
```




