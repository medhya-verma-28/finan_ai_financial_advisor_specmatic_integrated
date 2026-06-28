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

## Architecture of Specmatic Integration

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

```docker build -t finan-ml-app .```

This image contained:

Flask application

Trained ML models

Dependencies

API implementation

### Creating an Isolated Docker Network

To enable communication between containers, a dedicated Docker network was created.

Command:

```docker network create financial-test-net```

This network served as an isolated bridge through which the Flask application and the Specmatic container could communicate.


### Starting the Flask Application Container

The application container was launched inside the custom network.

Command:

```docker run -d --name flask-ml-app-service --network financial-test-net -p 5000:5000 finan-ml-app```

At this stage:

The Flask application was running inside Docker.

The service name "flask-ml-app-service" became accessible to other containers on the same network.

No external tunneling services were required.

### Executing Contract Tests Using the Specmatic Docker Image

Instead of installing Specmatic locally, the official Specmatic container was used.

The contracts directory and configuration file were mounted inside the container and tests were executed directly against the Flask container.

Command:

```docker run --rm --name specmatic-runner --network financial-test-net -v '${PWD}/contracts:/workspace/contracts' -v '${PWD}/specmatic.json:/workspace/specmatic.json' specmatic/specmatic:latest test '/workspace/contracts/openapi.yaml' --testBaseURL=http://flask-ml-app-service:5000```

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

## Why Schema Resiliency Tests Were Added

Traditional contract testing verifies whether an API implementation conforms to the expected specification at a particular point in time. While this ensures that producers and consumers remain aligned, it does not fully address the challenges introduced by evolving APIs and AI-driven applications.

As Finan AI Financial Advisor continues to evolve, API responses may occasionally contain additional optional fields, reordered properties, or non-breaking structural changes introduced during feature enhancements. Strict schema validation alone can sometimes cause these benign changes to be interpreted as failures, resulting in unnecessary maintenance overhead and brittle integrations.

Schema Resiliency Testing was therefore introduced to evaluate how well the API behaves under realistic schema evolution scenarios while still preserving backward compatibility guarantees. The objective was to ensure that consumers depending on the API would remain unaffected by additive and non-breaking modifications to the response structure.

The addition of Schema Resiliency Tests provides several advantages:

* Validation of API behavior under evolving schemas.
* Early detection of potentially breaking changes.
* Improved backward compatibility assurance.
* Increased confidence during feature releases and refactoring.
* Reduced integration fragility for API consumers.
* Stronger support for continuous delivery practices.

By complementing traditional contract testing with schema resiliency validation, the Finan AI Financial Advisor API becomes more robust, future-proof, and resilient to incremental changes introduced during development.

## Specmatic Schema Resiliency Tests Implementation Along with Contract Testing

After implementing only contract tests, following changes were made to the codebase:

- Added specmatic.yaml file to implement contract tests and schema resiliency tests together
- Added 400 Bad Request external example to include the scenario of null object request data
- Updated app.py and openapi.yaml based on the newly added external example

### Initial Test Failures

On running tests initially, automatic 415 Unsupported Media Type error was faced.

Command:

```docker run --rm --name specmatic-runner --network financial-test-net -v "${PWD}:/usr/src/app" specmatic/specmatic:latest test```

The result is shown below:

<img width="578" height="106" alt="WhatsApp Image 2026-06-26 at 1 58 26 PM" src="https://github.com/user-attachments/assets/f6275af2-f3ae-44cc-82bc-7d62c7653784" />

The above failed test was turned into a successful one by adding the 'force' argument in request.get_json() method to prevent the crashes.
Code implemention is shared below:

```data = request.get_json(force=True, silent=True) or {}```

On running tests again, 100% success was achieved.

<img width="648" height="91" alt="WhatsApp Image 2026-06-26 at 2 10 49 PM" src="https://github.com/user-attachments/assets/37236a7e-9871-4c2a-a7c0-582ec06801b9" />

## Separating Contract and Schema Resiliency Test Reports

Junit was used to separate both XML test reports.
Since the Specmatic version used in this project (Specmatic v2.48.0) does not allow to separate HTML test reports through run commands, we add a report folder directory variable in specmatic.yaml and set its value in run command of each test.

## Final Step-by-step Command Execution to Run Contract and Schema Resiliency Tests (Reports saved separately)

### Forcefully delete any running Docker containers with the same name:

```docker rm -f flask-ml-app-service```

### Build the latest Flask Application after pulling latest changes from this repo:

```docker build -t finan-ml-app .```

### Create a docker network:

```docker network create financial-test-net```

### Run Flask App Container:

```docker run -d --name flask-ml-app-service --network financial-test-net -p 5000:5000 finan-ml-app```

### Run Contract Tests and Save Report in build/reports/specmatic-contract-tests:

```docker run --rm --name specmatic-contract-runner --network financial-test-net -v "${PWD}:/usr/src/app" specmatic/specmatic:latest test --config=/usr/src/app/specmatic_contract.yaml --testBaseURL=http://flask-ml-app-service:5000 --junitReportDir=/usr/src/app/build/reports/specmatic-contract-tests/test/xml```

100% Success is achieved as follows:

Tests run: 3
Success: 3
Failed: 0
Skipped: 0
Error: 0
WIP: 0

### Run Schema Resiliency Tests and Save Report in build/reports/specmatic-resiliency-tests:

```docker run --rm --name specmatic-resiliency-runner --network financial-test-net -v "${PWD}:/usr/src/app" specmatic/specmatic:latest test --config=/usr/src/app/specmatic_resiliency.yaml --testBaseURL=http://flask-ml-app-service:5000 --junitReportDir=/usr/src/app/build/reports/specmatic-resiliency-tests/test/xml```

100% Success is achieved as follows:

Tests run: 3
Success: 3
Failed: 0
Skipped: 0
Error: 0
WIP: 0

FINALLY, BOTH CONTRACT AND SCHEMA RESILIENCY TESTS RAN SUCCESSFULLY!

TEST REPORTS HAVE BEEN SAVED IN SEPARATE DIRECTORIES AS WELL!

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

## Automating Contract Testing and Schema Resiliency Testing with GitHub Actions

Contract validation should not depend solely on manual execution.

Therefore, a CI workflow was configured using GitHub Actions.

Whenever code is pushed:

1. Workflow execution starts.

2. Dependencies are installed.

3. Contract tests and Schema Resiliency tests are executed.

4. Results are validated automatically.

This process ensures that future changes cannot unintentionally break API behavior.

The cloud runner executed the workflow successfully, confirming that the application remained compliant with its contract even outside the local development environment.

--------------------------------------------------------------------
