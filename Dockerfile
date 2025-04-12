FROM public.ecr.aws/lambda/python:3.11

# Install dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt

# Copy the rest of your project
COPY . . ${LAMBDA_TASK_ROOT}

# Set the Lambda entry point
CMD ["pycontrollers.lambdas.handle_post_sqs_lambda_handler.handler"]
