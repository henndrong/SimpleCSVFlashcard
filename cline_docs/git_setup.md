# Git Setup for Deployment

It looks like you're encountering an error when trying to push to GitHub. Let's fix that with a more detailed setup process.

## Complete Git Setup Instructions

Run these commands step by step:

```bash
# Navigate to your project folder
cd f:/Programming/Flashcard

# Initialize git (if not already done)
git init

# Add all files
git add .

# Create your initial commit
git commit -m "Initial commit"

# Check your current branch name
git branch
```

You'll likely see that your branch is named `master` rather than `main`. There are two ways to fix this:

### Option 1: Push to the existing branch name

```bash
# Push to GitHub using your current branch name (likely 'master')
git push -u origin master
```

### Option 2: Rename your branch to 'main' (recommended)

```bash
# Rename your local branch to 'main'
git branch -M main

# Push to GitHub using the new branch name
git push -u origin main
```

## If You're Still Having Issues

Try these steps:

```bash
# Verify your remote URL is correct
git remote -v

# If it's not correct, remove and add the proper URL
git remote remove origin
git remote add origin https://github.com/henndrong/SimpleCSVFlashcard.git

# Then try pushing again (with your correct branch name)
git branch -M main
git push -u origin main
```

## For Future Reference

When creating a new repository on GitHub, you can initialize it with:

```bash
# Clone the repository first (instead of git init)
git clone https://github.com/henndrong/SimpleCSVFlashcard.git
cd SimpleCSVFlashcard

# Then add your files, commit and push
git add .
git commit -m "Initial commit"
git push
```

This avoids branch naming issues because you're starting with GitHub's repository structure.
