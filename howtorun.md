# Project Setup Guide

Follow these steps to set up and run the project on your local machine.

## Step 1: Create a Virtual Environment

To isolate your project dependencies, create a virtual environment by running the following command:

### On Windows:

python -m venv venv

### On macOS/Linux:

python3 -m venv venv

## Step 2: Activate the Virtual Environment

After creating the virtual environment, activate it using the appropriate command below:

### On Windows:

venv\Scripts\activate

### On macOS/Linux:

source venv/bin/activate

Once activated, your command prompt should show the virtual environment name (e.g., (venv)).

## Step 3: Install Dependencies

With the virtual environment active, install all required dependencies by running:

pip install -r requirements.txt

This will install all necessary packages listed in the requirements.txt file.

## Step 4: Set Up Environment Variables

If your project requires environment variables, create a .env file in the root directory of your project. Here's how:

1. **Create a `.env` file** in the root directory of your project.
2. Add the necessary environment variables in the following format(check slack)
