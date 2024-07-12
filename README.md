# Lambda Cost Analysis

This is an open source  blank project for CDK development with TypeScript.
## Deployment Commands
1. Install CDK CLI V2
2. Bootstrap The CDK environment
3. Update the AWS_ACCOUNT and REGION variable under infrascture/lib/infrastructure.ts
4. cdk bootstrap ACCOUNT-NUMBER/REGION # e.g. cdk bootstrap 1111111111/us-east-1
5. cd infrastructure && cdk deploy --all

* `npm run build`   compile typescript to js
* `npm run watch`   watch for changes and compile
* `npm run test`    perform the jest unit tests
* `npx cdk deploy`  deploy this stack to your default AWS account/region
* `npx cdk diff`    compare deployed stack with current state
* `npx cdk synth`   emits the synthesized CloudFormation template
