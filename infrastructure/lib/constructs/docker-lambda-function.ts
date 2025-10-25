import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import {Construct} from 'constructs';
import {Duration} from 'aws-cdk-lib';
import * as path from 'path';

export interface DockerLambdaFunctionProps {
    /**
     * The handler for the Lambda function (e.g., 'backend.api.get_analysis_report.lambda_handler')
     */
    readonly handler: string;

    /**
     * Environment variables for the Lambda function
     */
    readonly environment?: { [key: string]: string };

    /**
     * Timeout for the Lambda function
     * @default Duration.seconds(29)
     */
    readonly timeout?: Duration;

    /**
     * Memory size for the Lambda function in MB
     * @default 128
     */
    readonly memorySize?: number;

    /**
     * Powertools service name for structured logging
     */
    readonly serviceName: string;

    /**
     * IAM role for the Lambda function
     * @default - a new role will be created
     */
    readonly role?: cdk.aws_iam.IRole;
}

/**
 * Shared construct for creating Docker-based Lambda functions with common configuration
 *
 * This construct provides:
 * - Docker-based deployment for consistent runtime environment
 * - AWS Lambda Powertools integration
 * - Common timeout and memory defaults
 */
export class DockerLambdaFunction extends lambda.DockerImageFunction {
    constructor(scope: Construct, id: string, props: DockerLambdaFunctionProps) {
        const dockerfilePath = path.join(__dirname, '..', '..', '..');

        super(scope, id, {
            code: lambda.DockerImageCode.fromImageAsset(dockerfilePath, {
                cmd: [props.handler],
                file: 'Dockerfile',
            }),
            timeout: props.timeout ?? Duration.seconds(29),
            memorySize: props.memorySize ?? 128,
            environment: {
                POWERTOOLS_SERVICE_NAME: props.serviceName,
                POWERTOOLS_LOG_LEVEL: 'INFO',
                POWERTOOLS_LOGGER_SAMPLE_RATE: '0.1',
                POWERTOOLS_METRICS_NAMESPACE: 'LambdaCostAnalysis',
                ...props.environment,
            },
            role: props.role,
        });
    }
}
