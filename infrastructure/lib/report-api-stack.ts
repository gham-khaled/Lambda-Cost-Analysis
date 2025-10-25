import * as cdk from 'aws-cdk-lib';
import {Construct} from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import {Aws, Duration} from "aws-cdk-lib";
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import {StateMachine} from "aws-cdk-lib/aws-stepfunctions";
import * as iam from 'aws-cdk-lib/aws-iam';
import {Bucket} from "aws-cdk-lib/aws-s3";
import * as ssm from "aws-cdk-lib/aws-ssm";
import {DockerLambdaFunction} from "./constructs/docker-lambda-function";

export interface ReportApiStackProps extends cdk.StackProps {
    readonly analysisStepFunction: StateMachine
    readonly analysisBucket: Bucket
}

export class ReportApiStack extends cdk.Stack {
    public api: apigateway.RestApi;

    constructor(scope: Construct, id: string, props: ReportApiStackProps) {
        super(scope, id, props);

        // Single Lambda function for all API routes
        const apiFunction = new DockerLambdaFunction(this, 'api_function', {
            handler: 'backend.api.app.lambda_handler',
            serviceName: 'lambda-cost-analysis-api',
            timeout: Duration.seconds(29),
            memorySize: 512,
            environment: {
                BUCKET_NAME: props.analysisBucket.bucketName
            }
        });

        // Grant permissions
        const listFunctionsPolicy = new iam.PolicyStatement({
            actions: ['lambda:ListFunctions'],
            resources: ['*'],
        });
        apiFunction.addToRolePolicy(listFunctionsPolicy);
        props.analysisBucket.grantRead(apiFunction);


        this.api = new apigateway.RestApi(this, 'analysisAPI', {
            defaultCorsPreflightOptions: {
                allowOrigins: apigateway.Cors.ALL_ORIGINS,
                allowMethods: apigateway.Cors.ALL_METHODS,
                allowHeaders: ['Content-Type', 'Authorization', 'X-Amz-Date', 'X-Api-Key', 'X-Amz-Security-Token', 'X-Amz-User-Agent'],
            }
        });

        // Use proxy integration to route all /api/* requests to the single Lambda
        const api_resource_prefix = this.api.root.addResource('api');
        const proxyResource = api_resource_prefix.addResource('{proxy+}');
        proxyResource.addMethod('ANY', new apigateway.LambdaIntegration(apiFunction));
        const apiGatewayRole = new iam.Role(this, 'ApiGatewayStepFunctionsRole', {
            assumedBy: new iam.ServicePrincipal('apigateway.amazonaws.com'),
            managedPolicies: [
                iam.ManagedPolicy.fromAwsManagedPolicyName('AWSStepFunctionsFullAccess'),
            ],
        });

        const startExecutionIntegration = new apigateway.AwsIntegration({
            service: 'states',
            action: 'StartExecution',
            options: {
                credentialsRole: apiGatewayRole,
                requestTemplates: {
                    'application/json': `{
            "input": "$util.escapeJavaScript($input.json('$'))",
            "stateMachineArn": "${props.analysisStepFunction.stateMachineArn}"
          }`
                },
                integrationResponses: [
                    {
                        responseParameters: {
                            'method.response.header.Access-Control-Allow-Origin': "'*'",
                        },
                        statusCode: '200',
                        responseTemplates: {
                            'application/json': `{
                "executionArn": "$input.path('$.executionArn')",
                "startDate": "$input.path('$.startDate')"
              }`
                        }
                    }
                ]
            }
        });
        const startExecutionResource = api_resource_prefix.addResource('startExecution');
        startExecutionResource.addMethod('POST', startExecutionIntegration, {
            methodResponses: [
                {
                    statusCode: '200',
                    responseParameters: {
                        'method.response.header.Access-Control-Allow-Origin': true,
                    }
                },

            ]
        });

        // TODO: Add request validation when integrating SF (Example: Lambda ARNs must be a non empty list)
    }
}
