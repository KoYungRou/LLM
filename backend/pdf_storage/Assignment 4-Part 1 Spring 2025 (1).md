# Assignment 4-Part 1 Spring 2025 (1)

## Page 1

Assignment 4 - Part 1
Due: March 14th 2025, 03:59 pm EST
Required Attestation and Contribution Declaration
● WE ATTEST THAT WE HAVEN’T USED ANY OTHER STUDENTS’ WORK IN OUR
ASSIGNMENT AND ABIDE BY THE POLICIES LISTED IN THE STUDENT
HANDBOOK.
● Contribution Example
○ Member 1: 33 1/3%
○ Member 2: 33 1/3%
○ Member 3: 33 1/3%
● Links to GitHub tasks and tasks owned by each member.
Assignment Overview
You had a wonderful Spring break and returned to your office with memories of beaches and
oceans from the beautiful warm city of Boston.. You are chilling by the office coffee machine
telling your colleagues how great the weather in Boston was the whole of last week and why
you enjoy the warm weather in Boston which you chose as your Spring break destination. Your
manager is obviously jealous of all this and asks your team to join her to discuss the next
project. She wants you to update the demo you put together for Assignment 1 with additional
capabilities! She says that she has been working with customers all week while you were away
on your break and wants to turn this project around in a week! You show your pictures from
Spring break and say with the warm weather you enjoyed last week, this assignment is a breeze
and you get ready! 🙂 & you are excited to get started!

## Page 2

Assignment Enhancement: Streamlit Application with
LLM Integration
Assignment Overview
You are enhancing your existing assignment 1 to develop a Streamlit
application that programmatically invokes Large Language Models (LLMs)
using FastAPI as an intermediary and LiteLLM for API management. The
application should build upon your existing progress and provide
functionality for summarizing and answering questions based on uploaded
PDF documents.
Assignment Objectives
1. Develop a Streamlit web application that:
○ Select previously parsed PDF content or new pdf files
○ Utilizes Large Language Models (LLMs) like GPT-4o through
LiteLLM to:
■ Provide summaries of the document content.
■ Answer user-submitted questions about the document
content.
2. Integrate FastAPI to handle backend API interactions between
Streamlit and LLM services.
3. Implement and manage API integrations with LiteLLM to simplify
connections to LLM providers.
Functional Requirements
Front-End (Streamlit)
● Create a user-friendly interface with the following features:
○ Select the LLM of choice
○ Ability to select from prior parsed pdf markdowns Or File
upload capability for new PDF documents.
○ Text input for asking specific questions.
○ Buttons to trigger summarization and Q&A functionalities.
○ Clear display areas for showing generated summaries and
answers.

## Page 3

Back-End (FastAPI)
● Set up REST API endpoints using FastAPI to manage requests from
the Streamlit application.
○ Endpoints:
■ /select_pdfcontent to select prior pdf parsed content
■ /upload_pdf to accept PDF content.
■ /summarize: Generates summaries.
■ /ask_question: Processes user questions and returns
answers.
● Implement appropriate response formats (JSON) for communication.
● Use Redis streams for communication between FASTAPI and other services
LiteLLM Integration
● Manage all interactions with various LLM APIs using LiteLLM.
● Clearly document and price model usage for input and output tokens
for every query.
● Include error handling for API calls and appropriate logging.
Deployment
● Use Docker compose and deploy all components on the cloud
Deliverables
1. GitHub Repository:
○ Well-organized, documented, and structured code.
○ Detailed project README.md including setup instructions.
○ Diagrammatic representations of architecture and data flows.
2. Documentation and Reporting
○ Create an AIUseDisclosure.md to transparently list and
explain all utilized AI tools and their specific applications within
the project.

## Page 4

Submission:
● Provide a GitHub repository link containing:
○ Project summary, PoC details, and documentation.
○ Clear task tracking using GitHub issues.
○ Technical and architectural diagrams illustrating the processing
and application flow.
○ A final, detailed Codelab outlining step-by-step implementation.
Number Model Documentation
1 GPT-4o OpenAI GPT-4o Documentation
Gemini - Google Gemini 2.0 Flash
2 Flash Documentation
3 DeepSeek DeepSeek LLM Documentation
4 Claude Anthropic Claude Documentation
5 Grok xAI Grok Documentation

