[//]: # (# Lambda Cost Analysis)

[//]: # ()

[//]: # (This is an open source  blank project for CDK development with TypeScript.)

[//]: # (## Deployment Commands)

[//]: # (1. Install CDK CLI V2)

[//]: # (2. Bootstrap The CDK environment)

[//]: # (3. Update the AWS_ACCOUNT and REGION variable under infrascture/lib/infrastructure.ts)

[//]: # (4. cdk bootstrap ACCOUNT-NUMBER/REGION # e.g. cdk bootstrap 1111111111/us-east-1)

[//]: # (5. cd infrastructure && cdk deploy --all)

[//]: # ()

[//]: # (* `npm run build`   compile typescript to js)

[//]: # (* `npm run watch`   watch for changes and compile)

[//]: # (* `npm run test`    perform the jest unit tests)

[//]: # (* `npx cdk deploy`  deploy this stack to your default AWS account/region)

[//]: # (* `npx cdk diff`    compare deployed stack with current state)

[//]: # (* `npx cdk synth`   emits the synthesized CloudFormation template)

[//]: # ()
# Lambda Cost Analysis

This project is an open-source template for AWS CDK development using TypeScript. It provides a starting point for
deploying AWS resources and includes example configurations and deployment commands. The primary focus is on analyzing
and managing costs associated with AWS Lambda functions.

## Features

- **TypeScript Support**: The project is set up with TypeScript for enhanced development experience.
- **CDK Integration**: Easily deploy AWS resources using AWS CDK.
- **Cost Analysis**: Built-in configurations to help analyze and optimize Lambda function costs.

Feel free to customize the project according to your needs and contribute improvements!

## Deployment Commands

To get started with deploying and managing your CDK stack, follow these steps:

1. **Install CDK CLI V2**

   Ensure that the AWS CDK CLI is installed. You can install it globally using npm:

   ```bash
   npm install -g aws-cdk@2
    ```
2. **Update Configuration**

Update the `AWS_ACCOUNT` and `REGION` variables in `infrastructure/lib/infrastructure.ts` to match your AWS account and
region.

3. **Bootstrap The CDK Environment**

    Prepare your AWS environment for CDK deployments. Do it only once.
   ```bash
   npm cdk bootstrap
    ```

## Parameters

| Parameter | Type   | Description                                                      | Mandatory                                 |
|-----------|--------|------------------------------------------------------------------|-------------------------------------------|
| `auth`    | String | Enable or disable basic auth (`True`/`False`).                   | Yes                                       |
| `username`| String | Username for basic auth.                                         | Yes, if `auth` is set to `True`           |
| `password`| String | Password for basic auth.                                         | Yes, if `auth` is set to `True`           |

## Bootstrapping Your CDK Environment

Before deploying the stack, you need to bootstrap your CDK environment. This step prepares your AWS environment for deploying resources using AWS CDK.

To bootstrap your environment, run the following command:

```bash
cdk bootstrap
```

## Deploying

To deploy this stack, you need to have AWS CDK installed and configured. Then run the following command:

```bash
cdk deploy --parameters auth=True --parameters username=YOUR_USERNAME --parameters password=YOUR_PASSWORD
```

## Retrieving Username and Password

If you forget the username or password, you can retrieve them by navigating to the AWS Management Console and checking
the environment variables of the deployed Lambda function. Follow these steps:

1. Open the [AWS Lambda Console](https://console.aws.amazon.com/lambda).
2. Select the deployed Lambda function from the list.
3. In the function's configuration tab, check the environment variables section to find the `USERNAME` and `PASSWORD`
   values.
   """
