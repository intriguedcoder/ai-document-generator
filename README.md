# AI-Assisted Document Authoring Platform

## Overview
A full-stack AI-powered web application that enables users to generate, refine, and export professional business documents (Word and PowerPoint) with iterative AI assistance using Google Gemini.

## Features
- 🔐 User authentication and project management
- 🤖 AI-powered outline generation (Bonus Feature)
- 📝 Context-aware content generation using Google Gemini
- ✨ Interactive refinement with prompts, feedback (like/dislike), and comments
- 📊 Version history with rollback capability
- 📥 Export to .docx and .pptx formats

## Tech Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **Google Firestore** - NoSQL database for user and project data
- **Google Gemini API** (gemini-2.5-flash) - LLM for content generation
- **python-docx** - Word document generation
- **python-pptx** - PowerPoint presentation generation
- **Firebase Auth** - User authentication

### Frontend
- **React + Vite** - Modern frontend framework
- **Chakra UI** - Component library
- **Axios** - HTTP client

## Architecture
The application follows a client-server architecture:
- **React SPA** communicates with FastAPI backend via REST API
- **FastAPI** processes requests and calls Google Gemini API for content generation
- **Firestore** stores users, projects, sections, versions, and feedback
- **Export service** assembles .docx/.pptx files from refined content



## Prerequisites

  - Python 3.9 or higher
  - Node.js 16 or higher
  - Google Cloud account with Gemini API access
  - Firebase project with Firestore and Authentication enabled

## Setup Instructions

### Backend Setup

1.  **Navigate to backend directory:**

   
    cd backend
   

2.  **Create and activate virtual environment:**

   
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
   

3.  **Install dependencies:**

   
    pip install -r requirements.txt
   

4.  **Create `.env` file in backend directory:**

   env
    GEMINI_API_KEY=your_gemini_api_key_here
    FIREBASE_PROJECT_ID=your_firebase_project_id
    GOOGLE_APPLICATION_CREDENTIALS=path/to/serviceAccountKey.json
   

5.  **Add Firebase service account credentials:**

      - Download `serviceAccountKey.json` from Firebase Console (Project Settings → Service Accounts)
      - Place it in the `backend/` directory
      - Update the path in `.env` file

6.  **Run the backend server:**

   
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   

    Backend will run at: `http://localhost:8000`
    API documentation: `http://localhost:8000/docs`

### Frontend Setup

1.  **Navigate to frontend directory:**

   
    cd frontend
   

2.  **Install dependencies:**

   
    npm install
   

3.  **Create `.env` file in frontend directory:**

   env
    VITE_API_BASE_URL=http://localhost:8000
    VITE_FIREBASE_API_KEY=your_firebase_api_key
    VITE_FIREBASE_AUTH_DOMAIN=your_auth_domain
    VITE_FIREBASE_PROJECT_ID=your_project_id
    VITE_FIREBASE_STORAGE_BUCKET=your_storage_bucket
    VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
    VITE_FIREBASE_APP_ID=your_app_id
   

4.  **Run the frontend development server:**

   
    npm run dev
   

    Frontend will run at: `http://localhost:5173`

## Usage Guide

### 1\. User Registration and Login

  - Open the application at `http://localhost:5173`
  - Register a new account or login with existing credentials
  - All projects are user-specific and private

### 2\. Create New Project

  - Click **"New Project"** from the dashboard
  - Select document type: **Word (.docx)** or **PowerPoint (.pptx)**
  - Enter project title and main topic/description

### 3\. Configure Document Structure

**Option A: AI-Generated Outline (Bonus Feature)**

  - Click **"AI-Suggest Outline"**
  - AI will generate section headers (Word) or slide titles (PowerPoint)
  - Review and edit the generated structure
  - Click **"Create Project & Start Editing"**

**Option B: Manual Configuration**

  - Click **"Add Section"** to manually create sections/slides
  - Enter title and description for each
  - Click **"Create Project & Start Editing"**

### 4\. Generate Content

  - Navigate to the document editor
  - Click **"Generate Content with AI"** for each section/slide
  - AI generates context-aware content based on your project topic and section title

### 5\. Refine Content Iteratively

  - Enter refinement prompts in the text box (e.g., "Make this more formal", "Add bullet points")
  - Click **"Refine with AI"** to apply changes
  - Click **Like** or **Dislike** to provide feedback
  - Add **comments** for personal notes
  - View **version history** to see all changes
  - Click **"Revert to this version"** to restore previous content

### 6\. Export Document

  - Click **"Save Changes"** to persist all edits
  - Click **"Export DOCX"** for Word documents or **"Export PPTX"** for PowerPoint presentations
  - Download opens automatically - open in Microsoft Office

## Usage Examples

### Sample Topics

**Word Documents:**

  - "Market analysis of the electric vehicle industry in 2025"
  - "Quarterly business report for Q4 2024"
  - "Comprehensive study on renewable energy trends"
  - "Product requirements document for mobile app"

**PowerPoint Presentations:**

  - "Product launch presentation for SaaS platform"
  - "AI technology trends and industry impact"
  - "Company overview for investor pitch deck"
  - "Training workshop on digital marketing strategies"

### Sample Refinement Prompts

  - "Make this more professional and formal"
  - "Convert paragraphs to bullet points"
  - "Shorten to 150 words"
  - "Add specific statistics and data points"
  - "Make it more engaging and conversational"
  - "Use simpler language for a general audience"
  - "Add examples to illustrate key concepts"
  - "Expand with more details and context"

## Project Structure


ai-document-generator/
├── backend/
│   ├── app/
│   │   ├── core/           # Configuration and dependencies
│   │   │   ├── config.py
│   │   │   └── dependencies.py
│   │   ├── models/         # Pydantic schemas
│   │   │   └── schemas.py
│   │   ├── routers/        # API endpoints
│   │   │   ├── auth.py
│   │   │   ├── projects.py
│   │   │   ├── generate.py
│   │   │   └── refinement.py
│   │   ├── services/       # Business logic
│   │   │   ├── gemini_service.py
│   │   │   └── export_service.py
│   │   └── utils/          # Utilities
│   │       ├── firebase_client.py
│   │       └── logger.py
│   ├── requirements.txt
│   ├── .env
│   └── .gitignore
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── auth/          # Login/Register components
│   │   │   ├── configuration/ # Project configuration
│   │   │   ├── dashboard/     # Project list
│   │   │   └── editor/        # Document editor
│   │   ├── pages/
│   │   ├── services/
│   │   │   └── api.js         # API client
│   │   └── App.jsx
│   ├── package.json
│   ├── .env
│   └── .gitignore
└── README.md


## Demo Video

📹 **[Watch Demo Video on Google Drive](https://www.google.com/search?q=YOUR_DRIVE_LINK_HERE)**

The demo video includes:

  - Architecture and code walkthrough
  - User registration and authentication
  - Word document creation workflow with AI outline
  - PowerPoint presentation workflow with AI outline
  - Content generation and refinement features
  - Like/Dislike feedback and comments
  - Version history and rollback
  - Export functionality demonstration

## Deployment (Optional)

If deployed, add URLs here:

  - **Backend API:** [Deployment URL]
  - **Frontend App:** [Deployment URL]

## Challenges & Learnings

### Challenges Faced

1.  **LLM Response Consistency:** The Gemini API sometimes included markdown formatting (bold/italic markers) and introductory phrases like "Here is the content for your slides". Solved by implementing robust text cleaning with regex to remove unwanted formatting and normalize bullet points.
2.  **Document Export Formatting:** Ensuring proper formatting in generated .docx and .pptx files required careful use of python-docx and python-pptx libraries, especially for maintaining consistent styling and handling different content types (paragraphs vs bullet points).
3.  **Version History Management:** Managing refinement history with multiple versions per section required careful database schema design in Firestore to track changes efficiently while maintaining performance.
4.  **State Management:** Handling complex state across multiple steps (configuration → generation → refinement) in React required careful component design and proper state lifting.

### Key Learnings

  - **Prompt Engineering:** Learned how to craft effective prompts for LLMs to generate consistent, high-quality content. Adding explicit instructions like "Do NOT include introductory text" significantly improved output quality.
  - **FastAPI Integration:** Gained experience building async REST APIs with FastAPI and integrating external AI services. Learned to handle streaming responses and manage API rate limits.
  - **State Management:** Improved skills in managing complex React state for multi-step workflows and version control. Used proper lifting state and context where needed.
  - **NoSQL Database Design:** Learned to structure Firestore collections for hierarchical data (projects → sections → versions → feedback) with efficient querying patterns.
  - **Error Handling:** Implemented comprehensive error handling for AI API failures with graceful fallbacks to ensure user experience isn't disrupted.

## Future Enhancements

  - Real-time collaboration on documents with multiple users
  - Additional document templates (reports, proposals, resumes, business plans)
  - Advanced formatting options (charts, images, tables, custom styles)
  - Multi-language content generation support
  - Team workspace and project sharing features
  - Integration with Google Docs and Microsoft 365
  - Export to PDF format
  - AI-powered grammar and style checking
  - Template library with pre-built document structures
  - Analytics dashboard showing usage patterns and AI performance

