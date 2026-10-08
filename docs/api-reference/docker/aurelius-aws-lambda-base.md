# aurelius-aws-lambda-base

[![SonarQube Cloud](https://sonarcloud.io/images/project_badges/sonarcloud-light.svg)](https://sonarcloud.io/summary/new_code?id=aurelius-aws-lambda-base)

This Docker image provides a base for all AWS Lambda functions. It provides all necessary dependencies to run
Lambda functions based on Python.

??? QUESTION "Why not use the official AWS Lambda Python image?"

    While the official AWS Lambda Python image is a good starting point, it has a significantly larger size than this image.

## Structure

This Docker image provides the following key dependencies for Lambda functions based on Python:

- **Python**: This is the Python runtime used for executing your Lambda functions. Its version is pinned in
  the image's `Dockerfile`.
- [**AWS Lambda Runtime Interface Client**](https://github.com/aws/aws-lambda-python-runtime-interface-client):
  This is used to communicate with the AWS Lambda service.
- [**AWS Lambda Insights Extension**](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Lambda-Insights.html):
  This is used by AWS CloudWatch to collect metrics and logs from your Lambda function.

It also sets the `ENTRYPOINT` for the Docker image to the AWS Lambda Runtime Interface Client, which is necessary
for the Lambda function to start correctly.

## Usage

Follow the steps below to use this Docker image as part of a Lambda function:

### Dockerfile

Start your `Dockerfile` with the following line:

```dockerfile
FROM aurelius-aws-lambda-base:local
```

Next, you can add your Python code and any additional dependencies.

Finalize your Dockerfile by specifying the `CMD` instruction. This should point to the main entrypoint of your
Lambda function.

??? EXAMPLE "`CMD` instruction"

    If your Lambda function is defined in a module named `app.py` and the handler function is `lambda_handler`, you would add:

    ```dockerfile
    CMD ["app.lambda_handler"]
    ```

### Project Configuration

To ensure that the `aurelius-aws-lambda-base` image is built before your Lambda function, add the following line
to your `project.json` file:

```json
{
    "implicitDependencies": ["aurelius-aws-lambda-base"]
}
```
