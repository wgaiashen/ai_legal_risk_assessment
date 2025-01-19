# Legal Risk Assessment Tool: 
## _Using AI to Assess AI_

### Video Demo: see [here](https://youtu.be/-esWFN2BpFo).

### Table of Contents
- [Overview](#overview)
- [Key features](#key-features)
- [Installation](#installation)
- [Usage instructions](#usage-instructions)
- [File Structure](#file-structure)
- [Risk factors assessed](#risk-factors-assessed)
- [Technologies used](#technologies-used)
- [Future enhancements](#future-enhancements)
- [Background](#background)
- [Acknowledgments](#acknowledgments)

## Overview
This project is my CS50 final project. The purpose of this project is to _use_ AI to provide a legal risk assessment _of_ an AI product. 

Lawyers regularly advise clients on the legal risks associated with deploying an AI-enabled tool, product or service ("AI product") within their organisation or externally to customers. This tool seeks to automate this process to help clients assess the legal risks of AI products they are proposing to deploy. 

Starting with the user's textual description of the AI feature, this tool uses a large language model to assess the potential legal risks associated with using the AI product. After logging in, the user engages in a chat-based conversation with the LLM where the LLM aims to best understand the user's proposed product. After this, the tool returns a thorough assessment highlighting the level of risk associated with 10 different legal risk factors. It also provides actionable recommendations for risk mitigation and a total risk score out of 100 to enable users to escalate risks appropriately.

The code in this repository is written in Python using Flask for the web application, accompanied by HTML. 

## Key features
- **Interactive chat interface:** users can interactively in freeform provide details about their AI product, to simulate an interaction between an expert human lawyer and a client. This is implemented as a chat using a customized prompt with a Gemini model, accessed through Google's Gemini API.
- **Comprehensive risk analysis:** the model assesses 10 key risk factors, such as training data, transparency and operational risks. For each factor, a risk level (very high, high, medium or low) is returned along with a justification. Each factor's risk level is defined and provided to the model to guide its assessment.
- **User authentication:** supports user registration and login to manage access securely. This utilizes SQLite with Flask.
- **User-friendly web interface:** web interface geared towards non-technical users and implemented through a modular template structure with Jinja2 to streamline front-end development.

## Installation

1. **Clone the repository**
    ```bash
    git clone https://github.com/wgaiashen/ai_assessment_tool.git
    cd ai_assessment_tool
    ```

2. **Setup the virtual environment**
    ```bash
    python3.9 -m venv <venv name>
    source <venv name>/bin/activate
    ```

3. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4. **Setup the database**
    ```bash
    flask db init
    flask db migrate
    flask db upgrade
    ```

5. **Run the application**
    ```bash
    flask run
    ```

6. **Access the application**
    Open your browser and navigate to `http://127.0.0.1:5000`.

## Usage instructions

Once running:
1. Create an account to access the tool.
2. Use your credentials to log in securely.
3. Describe the AI system being evaluated, including its purpose and intended usage.
4. Answer any potential clarifying questions to refine the model's risk analysis.
5. Access a detailed summary of risks and recommendations in the results section.

## File Structure

### Core Application Files
- **`app.py`**: Contains the main application logic and routes.
- **`risk_factors.py`**: Contains details of the risk factors and criteria for each lever to calibrate the LLM.
- **`risk_assessment.db`**: SQLite database for storing user and assessment data.

### Templates
- **`templates/base.html`**: Base layout template for all pages.
- **`templates/landing.html`**: Homepage template.
- **`templates/login.html`**: Login page template.
- **`templates/register.html`**: Registration page template.
- **`templates/chat.html`**: Chat interface template.
- **`templates/results.html`**: Risk assessment results page template.

### Static Files
- **`static/styles.css`**: Contains the custom CSS for styling the application.

### Miscellaneous
- **`requirements.txt`**: List of Python dependencies.

## Risk factors assessed
1. Bias and Fairness
2. Data Processed
3. Legal and Regulatory Compliance
4. Operational Risk
5. Reputational Risk
6. Technology
7. Training Data
8. Transparency
9. Use and Functionality
10. User and Audience

## Technologies used
- **Backend:** Flask
- **Frontend:** HTML, CSS, Jinja2 templates
- **Database:** SQLite
- **Large language model:** Google Gemini API

## Future enhancements
- **Support for multi-language assessments:** to cater to a global audience.
- **Advanced analytics:** visualize risks and trends over time.
- **Custom risk factors:** allow users to define their own assessment criteria.
- **Add unit tests.** 

## Background
Over the last several years as a technology lawyer , I have been helping clients navigate the risks of deploying machine learning systems in their organisations – whether to boost productivity internally or to supplement their product offering externally. Most of these engagements follow a familiar pattern: collecting relevant inputs (i.e. the client’s description of the AI tool they are proposing to use), conducting structured assessments of the legal risks involved, and producing actionable recommendations for mitigating such risks. This project is my attempt at doing so.

## Acknowledgments
This project was built as the final submission to the HarvardX [CS50x 2024](https://cs50.harvard.edu/x/2024/) course. 

---
For any questions or contributions, please contact [wgaiashen@gmail.com].

