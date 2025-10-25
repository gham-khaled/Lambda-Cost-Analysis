import * as lambda from 'aws-cdk-lib/aws-lambda';
import {Construct} from 'constructs';
import {Duration} from 'aws-cdk-lib';
import * as path from 'path';

export interface DockerLambdaFunctionProps extends Omit<lambda.DockerImageFunctionProps, 'code'> {
    /**
     * The handler for the Lambda function (e.g., 'backend.api.get_analysis_report.lambda_handler')
     */
    readonly handler: string;

    /**
     * Powertools service name for structured logging
     */
    readonly serviceName: string;
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
        const { handler, serviceName, ...rest } = props;
        const dockerfilePath = path.join(__dirname, '..', '..', '..');

        super(scope, id, {
            // Default configurations
            timeout: Duration.seconds(29),
            memorySize: 128,
            architecture: lambda.Architecture.ARM_64,

            // Spread remaining props to allow overrides
            ...rest,

            // Docker image configuration with handler override
            code: lambda.DockerImageCode.fromImageAsset(dockerfilePath, {
                file: 'Dockerfile',
                cmd: [handler],
            }),

            // Merge environment variables (user props override defaults)
            environment: {
                POWERTOOLS_SERVICE_NAME: serviceName,
                POWERTOOLS_LOG_LEVEL: 'INFO',
                POWERTOOLS_LOGGER_SAMPLE_RATE: '0.1',
                POWERTOOLS_METRICS_NAMESPACE: 'LambdaCostAnalysis',
                ...rest.environment,
            },
        });
    }
}
