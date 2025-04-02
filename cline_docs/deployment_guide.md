# IoT Flashcard Quiz Deployment Guide

This guide will help you deploy your Streamlit flashcard application to the internet so you can access it from any device.

## Option 1: Streamlit Cloud (Recommended)

Streamlit Cloud is the easiest way to deploy your Streamlit app. It's free for personal use with some limitations.

### Step 1: Set up a GitHub Repository

1. Create a GitHub account if you don't have one: [GitHub Sign Up](https://github.com/join)
2. Create a new repository:
   - Go to [GitHub New Repository](https://github.com/new)
   - Name your repository (e.g., "iot-flashcards")
   - Make it public or private
   - Click "Create repository"

3. Push your code to GitHub (using terminal/command prompt):
   ```bash
   # Navigate to your project folder
   cd f:/Programming/Flashcard
   
   # Initialize git if not already done
   git init
   
   # Add all files
   git add .
   
   # Commit changes
   git commit -m "Initial commit"
   
   # Link to your GitHub repository (replace YOUR_USERNAME with your GitHub username)
   git remote add origin https://github.com/YOUR_USERNAME/iot-flashcards.git
   
   # Push to GitHub
   git push -u origin main
   ```

### Step 2: Create requirements.txt

Ensure your project has a `requirements.txt` file with all dependencies:

```
streamlit==1.31.0
pandas==2.2.0
```

### Step 3: Deploy to Streamlit Cloud

1. Go to [Streamlit Cloud](https://streamlit.io/cloud)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository, branch, and main file (`app.py`)
5. Click "Deploy"

Your app will be deployed in a few minutes and will have a URL like `https://username-iot-flashcards-app-abc123.streamlit.app`

## Option 2: Hugging Face Spaces

Hugging Face Spaces is another excellent platform for deploying Streamlit apps.

### Step 1: Set up a Hugging Face Account

1. Sign up at [Hugging Face](https://huggingface.co/join)

### Step 2: Create a New Space

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click "Create Space"
3. Choose a name for your space (e.g., "iot-flashcards")
4. Select "Streamlit" as the SDK
5. Set visibility (Public or Private)
6. Click "Create Space"

### Step 3: Upload Files

You can upload files through the web interface or use Git:

```bash
# Clone your space repository
git clone https://huggingface.co/spaces/YOUR_USERNAME/iot-flashcards

# Copy your files to the cloned repository
# (Make sure to include app.py, requirements.txt, and your CSV data file)

# Add files, commit and push
cd iot-flashcards
git add .
git commit -m "Initial commit"
git push
```

## Option 3: Railway (Alternative Cloud Platform)

Railway is a modern cloud platform that makes deployment simple.

### Step 1: Set up a GitHub Repository
Follow the same steps as in Option 1, Step 1.

### Step 2: Sign up for Railway

1. Go to [Railway](https://railway.app/)
2. Sign up using GitHub

### Step 3: Create a New Project

1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your flashcard application repository
4. Railway will detect your Streamlit app and deploy it

## Accessing Your Deployed App

Once deployed, you can access your app from any device with internet access:
- On your phone: Simply open the app URL in your mobile browser
- On your laptop: Open the URL in any web browser

## Important Considerations

1. **Data Files**: Make sure your CSV data file (`iot_flashcards_v2.csv`) is included in your repository.

2. **Privacy**: If your flashcards contain sensitive information, consider using a private repository and deployment.

3. **Updates**: When you make changes to your app:
   - Commit and push changes to GitHub
   - Streamlit Cloud will automatically redeploy
   - For Hugging Face, push to your space repository
   - For Railway, push to your GitHub repository

4. **Costs**: 
   - Streamlit Cloud: Free tier with limitations
   - Hugging Face Spaces: Free for public spaces
   - Railway: Free tier with $5 credit per month

## Need Help?

- [Streamlit Documentation](https://docs.streamlit.io/streamlit-cloud/get-started)
- [Hugging Face Spaces Documentation](https://huggingface.co/docs/hub/spaces)
- [Railway Documentation](https://docs.railway.app/)
