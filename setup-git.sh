#!/bin/bash
# ==========================================
# hans-ai-mem0 - Git Setup Script
# ==========================================

REPO_NAME="hans-ai-mem0"
GITHUB_USER="HemantLaravel"
GITHUB_REPO="https://github.com/$GITHUB_USER/$REPO_NAME.git"

echo "🔧 Setting up Git for $REPO_NAME..."
echo ""

# Configure git
git config user.name "Hemant Kumar"
git config user.email "hemant@example.com"

# Add remote
git remote add origin $GITHUB_REPO

# Create main branch
git checkout -b main

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit - Hans AI Mem0 Server

- Memory management server using Mem0 with Qdrant backend
- Semantic search capabilities
- RESTful API for memory operations
- Docker-ready deployment

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
"

echo "✅ Git initialized for $REPO_NAME"
echo ""
echo "🚀 To push to GitHub, run:"
echo "   git push -u origin main"
echo ""
echo "📁 Repository: https://github.com/$GITHUB_USER/$REPO_NAME"