## Introduction to Specmatic

Specmatic is an OpenAPI-driven contract testing framework that automatically validates APIs against their specifications.

Specmatic provides capabilities such as:

Contract validation

Automatic test generation

Mock server creation

Backward compatibility verification

CI/CD integration

Docker support

Because Specmatic supports containerized execution, no local installation was required.

--------------------------------------------------------------------

## My Personal Project: Finan-AI Financial Advisor

### (Recognised by GirlScript Summer of Code'26)

### (Pull Request Link: https://github.com/Niketkumardheeryan/ML-CaPsule/pull/1926)

### 🌐 Live Web Application

🔗 **[https://finan-ai-financial-advisor.onrender.com](https://finan-ai-financial-advisor.onrender.com)**

---

### Project Real Time Screen Recording

<video src="https://github.com/user-attachments/assets/c948476b-65f3-4bec-b683-51808127392b" width="100%" controls></video>

### Personal Repository:

https://github.com/medhya-verma-28/finan_ai_financial_advisor

### Problem Statement:

In India, living in metropolitan cities, big dreams, even FOMO or lack of financial literacy– there can be so many reasons because of which people suffer in managing their finances and then end up in financial crisis like debt trap, bankruptcy etc, leading to compromised financial security in future, or even hand-to-mouth situation.

### Proposed Solution:

An AI-Powered Financial Advisor that informs user about their current financial status (based on monthly income, expenditure and debt status). It also advices user on how to enhance their finance management skills and upgrade their financial status.

X-factor: Model would be trained according to Indian economic landscape. Financial status prediction and financial advice would be useful for Indian users.

### Project Features:

Financial State Prediction:

Uses a trained machine learning model built on an Indian finance dataset.
Predicts users' financial conditions based on:
Monthly income
Cost of living expenditure
Investment expenditure
Consumerist expenditure
Crisis-related expenses
Debt status

India-Centric Financial Intelligence:

Dataset reflects Indian economic and spending patterns.
Models various financial categories such as:
High-rate savers
Low-rate savers
Deficit living
Zero Balance Living

The objective was to provide users with an interactive financial advisory assistant that transforms raw financial inputs into actionable insights.

### Project Technology Stack:

Backend

- Flask

Machine Learning

- Scikit-learn

- Random Forest Regressor

- SVC Classifier

Frontend

- HTML

- CSS

- JavaScript

Data Processing

- Pandas

- NumPy

Text Response API

- Gemini API

Deployment

- Render

Contract Testing

- Specmatic Studio

- OpenAPI Specification

CI/CD

- GitHub Actions

--------------------------------------------------------------------

## Why Contract Testing Was Added

Although the application was functioning correctly, API contracts had not yet been formally validated.

Potential issues included:

- Incorrect HTTP status codes.

- Unexpected response structures.

- Value mismatches.

- Breaking changes after future modifications.

Therefore, Specmatic contract testing was incorporated to enforce API correctness.

--------------------------------------------------------------------

## Architecture of Contract Validation

API Contract & Examples

↓

Flask Application

↓

Docker Container

↓

Isolated Docker Network

↓

OpenAPI Contract Validation

↓

GitHub Actions CI Pipeline

--------------------------------------------------------------------

## Specmatic Contract Testing Implementation:

### Creating the API Contract & Examples

An OpenAPI specification file named:

openapi.yaml

was created to formally describe the API behaviour.

The specification included:

POST /analyze endpoint

Request schema

Response schema

Required properties

Status codes

Enum values

The specification acted as the source of truth for API behaviour.

Also, mock contract examples were also generated and stored for as JSON files in openapi_examples folder for contract testing.

### Containerizing the Flask Application

The application was first packaged into a Docker image.

Building the image:

docker build -t finan-ml-app .

This image contained:

Flask application

Trained ML models

Dependencies

API implementation

### Creating an Isolated Docker Network

To enable communication between containers, a dedicated Docker network was created.

Command:

docker network create financial-test-net

This network served as an isolated bridge through which the Flask application and the Specmatic container could communicate.


### Starting the Flask Application Container

The application container was launched inside the custom network.

Command:

docker run -d --name flask-ml-app-service --network financial-test-net -p 5000:5000 finan-ml-app

At this stage:

The Flask application was running inside Docker.

The service name "flask-ml-app-service" became accessible to other containers on the same network.

No external tunneling services were required.

### Executing Contract Tests Using the Specmatic Docker Image

Instead of installing Specmatic locally, the official Specmatic container was used.

The contracts directory and configuration file were mounted inside the container and tests were executed directly against the Flask container.

Command:

docker run --rm --name specmatic-runner --network financial-test-net `

-v "${PWD}/contracts:/workspace/contracts" `

-v "${PWD}/specmatic.json:/workspace/specmatic.json" `

specmatic/specmatic:latest test "/workspace/contracts/openapi.yaml" --testBaseURL=http://flask-ml-app-service:5000

During execution, Specmatic performed the following operations:

Loaded openapi.yaml.

Generated test scenarios automatically.

Sent requests to the Flask API container.

Compared responses with the specification.

Reported mismatches whenever deviations were detected.

Because both containers belonged to the same Docker network, communication occurred entirely inside Docker without exposing the application externally.

--------------------------------------------------------------------

## Initial Contract Failures

During early executions, several inconsistencies were discovered.

### Failure 1: HTTP Status Mismatch

Specmatic reported:

R0002: HTTP status mismatch

Specmatic expected:

200 OK

However, the API returned:

500 Internal Server Error

The validation output indicated:

"Specification expected status 200 but response contained status 500."

This issue demonstrated that the implementation and contract were inconsistent.

The backend code in app.py was investigated.

The condition checking whether Gemini API key exists or not, was removed from app.py as contract testing generates mock requests, so API key is not required.

This condition was responsible for sending 500 status which failed the contract test.

Thus, after app.py was corrected, the endpoint consistently returned the expected status code and the status mismatch was resolved.

### Failure 2: Value Mismatch

Once the status issue had been fixed, another contract violation appeared.

Specmatic reported:

R1002: Value mismatch

The specification expected one of:

- High-Rate Saver (>=25% in savings)

- Zero-Balance Living

- Low-Rate Saver (<25% in savings)

- Deficit Living

However, the API returned:

Stable

The response field:

predictions.financial_state_category

did not conform to the values defined in the OpenAPI contract.

This mismatch clearly illustrated one of the major advantages of contract testing: even though the endpoint was operational, the response semantics were inconsistent with the specification.

--------------------------------------------------------------------

## Bringing the Specification and Implementation into Alignment

To eliminate the mismatch, modifications were introduced in:

openapi.yaml

The contract definitions were refined to represent the expected response schema.

app.py

The response generation logic was updated so that the output matched the values defined by the specification.

Particular attention was paid to:

- Response structure.

- Status codes.

- Nested JSON fields.

- Enumerated category values.

By synchronizing both files, the implementation and contract were brought into agreement.

--------------------------------------------------------------------

## Achieving Successful Contract Validation

After the changes had been introduced, the tests were executed again.

Specmatic Studio reported:

Tests run: 2

Success: 2

Failed: 0

Errors: 0

Skipped: 0

Coverage: 100%

The /analyze endpoint achieved complete contract coverage.

The successful execution confirmed that:

- Response schema was correct.

- Status codes matched.

- Enumerated values were valid.

- API behavior complied with the OpenAPI specification.

Thus, all contract tests ran successfully on local.

--------------------------------------------------------------------

## Pushing the Changes to GitHub

A dedicated repository was created for the Specmatic-enabled version:

https://github.com/medhya-verma-28/finan_ai_financial_advisor_specmatic_integrated

The repository contains:

- Flask application.

- Docker configuration.

- OpenAPI specification.

- Specmatic setup.

- GitHub Actions workflow.

--------------------------------------------------------------------

## Automating Contract Testing with GitHub Actions

Contract validation should not depend solely on manual execution.

Therefore, a CI workflow was configured using GitHub Actions.

Whenever code is pushed:

1. Workflow execution starts.

2. Dependencies are installed.

3. Contract tests are executed.

4. Results are validated automatically.

This process ensures that future changes cannot unintentionally break API behavior.

The cloud runner executed the workflow successfully, confirming that the application remained compliant with its contract even outside the local development environment.

--------------------------------------------------------------------
