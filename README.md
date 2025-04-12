# Building Clash Detection System

This repository contains the implementation of the Building Clash Detection System, designed to identify clashes between building features based on their elevation, height, and geographical coordinates.

## Project Overview

The Building Clash Detection System checks for clashes or overlaps between building features. The system processes input in the form of geographical data (GeoJSON), calculates potential clashes, and outputs results including details about the buildings involved and the extent of the clash.


## Installation

To get started with this project, clone the repository and set up the required environment.

### 1. Clone the Repository

git clone https://github.com/AnushaDhanashekar/building-clash-detection-system.git

###2. Install Dependencies
The project requires the following dependencies:

Docker

AWS CDK

AWS CLI

# Docker
To use Docker, ensure it is installed on your machine. If not, follow the official installation guide: Docker Installation Guide

# AWS CDK and AWS CLI
Install the AWS CDK and AWS CLI globally if not already installed.

# Install AWS CLI (if not installed)
pip install awscli

# Install AWS CDK
npm install -g aws-cdk
After installing AWS CLI, configure your AWS credentials with the following command:

aws configure
You will need to input your AWS Access Key ID, AWS Secret Access Key, Default region name, and Default output format.

3. Build Docker Image
Once the project is cloned and dependencies are set up, proceed with the Docker build.

# Build the Docker image
docker build -t building-clash-detection .

4. Run Docker Container Locally
After building the Docker image, run the container to check the system locally.

# Run the Docker container
docker run -p 8080:8080 building-clash-detection
This will start the service on port 8080 on your local machine. You can now test the service locally.

5. Deploy with AWS CDK
Now, deploy the application using AWS CDK.

Bootstrap the environment (if not done already):
cdk bootstrap

Deploy the CDK stack:
cdk deploy
This will deploy the stack and provision resources on AWS.

6. Access API Gateway and Execute POST Request
Once the CDK deployment is complete, you can access the API Gateway that was created for your service.

Go to the AWS Management Console.

Open the API Gateway service and find the API created by the CDK deployment.

Copy the Invoke URL for the API.

You can now execute a POST request to this URL using any tool like Postman or curl.

Example cURL Command:

curl -X POST https://<your-api-gateway-id>.execute-api.<region>.amazonaws.com/<stage>/clash-detection \
    -H "Content-Type: application/json" \
    -d '{
          "task_id": "test-task-id",
          "input": {
            "features": [
              {
                "type": "Feature",
                "id": "building_0",
                "properties": {"height": 4, "elevation": 0},
                "geometry": {
                  "type": "Polygon",
                  "coordinates": [[[20, 0], [20, 60], [0, 60], [0, 0], [20, 0]]]
                }
              },
              {
                "type": "Feature",
                "id": "building_1",
                "properties": {"height": 4, "elevation": 2},
                "geometry": {
                  "type": "Polygon",
                  "coordinates": [[[60, 60], [0, 60], [0, 40], [60, 40], [60, 60]]]
                }
              }
            ]
          }
        }'
This will send a POST request to the deployed API and trigger the clash detection process.

Python Virtual Environment Commands
Create a virtual environment:

python3 -m venv venv
Activate virtual environment:

# On Windows
venv\Scripts\activate

# On MacOS/Linux
source venv/bin/activate

Install dependencies from requirements.txt:
pip install -r requirements.txt

