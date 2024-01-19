# pilotchatbot
General aviation pilot chatbot and document extractor using LLM

# Installation

# DEV scripts in .pynb using Conda environment

# Creating a Virtual Environment and Installing Packages using Conda on Windows


## Step 1: Open Anaconda Prompt

1. Search for "Anaconda Prompt" in the Windows Start menu.
2. Right-click on it and select "Run as administrator".

## Step 2: Create a New Conda Environment

1. To create a new environment, use the following command:

```bash

conda create --prefix ./pilotbotenv python=3.11.0

conda activate pilotbotenv
```


## Step 3: Activate the New Environment

Activate your newly created environment:

```bash

conda activate ./pilotbotenv
```


## Step 5: Install Packages from requirements.txt

Install all required packages:

```bash

pip install -r requirements.txt

    This will install the packages and their specific versions listed in your requirements.txt.
```


Launch Jupyter Notebook:

```bash

jupyter notebook
```

## Step 7: Deactivate the Environment (When Done)

Once you are done working, deactivate the environment:
```bash

conda deactivate
```