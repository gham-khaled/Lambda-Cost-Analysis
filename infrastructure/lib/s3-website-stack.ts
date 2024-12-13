import * as cdk from "aws-cdk-lib";
import {Construct} from "constructs";
import {Bucket} from "aws-cdk-lib/aws-s3";
import {BucketDeployment, Source} from "aws-cdk-lib/aws-s3-deployment";
import {
    AllowedMethods, CachePolicy, CloudFrontAllowedMethods,
    CloudFrontWebDistribution,
    Distribution, LambdaEdgeEventType,
    OriginAccessIdentity, OriginProtocolPolicy, OriginRequestPolicy,
    ViewerProtocolPolicy
} from "aws-cdk-lib/aws-cloudfront";
import {CfnOutput, Duration} from "aws-cdk-lib";
import * as apigateway from "aws-cdk-lib/aws-apigateway";
import {HttpOrigin, S3Origin} from "aws-cdk-lib/aws-cloudfront-origins";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as iam from 'aws-cdk-lib/aws-iam';

export class S3WebsiteStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props: cdk.StackProps, api: apigateway.RestApi, authLambda: lambda.Function) {
        super(scope, id, props);

        const bucket = new Bucket(this, 'analysis-website', {
            // websiteIndexDocument: 'index.html',
            publicReadAccess: false,
            autoDeleteObjects: true,
            removalPolicy: cdk.RemovalPolicy.DESTROY
        });

        new BucketDeployment(this, 'MyDeployment', {
            sources: [Source.asset('../frontend/dist/')],
            destinationBucket: bucket,
        });
        const cloudfrontOAI = new OriginAccessIdentity(this, 'cloudfront-OAI');
        bucket.grantRead(cloudfrontOAI);


        const s3Origin = new S3Origin(bucket, {originAccessIdentity: cloudfrontOAI})

        const apiOriginName = `${api.restApiId}.execute-api.${this.region}.amazonaws.com`;

        // origin path must be set to the stage name, and this assumes that after
        // the path there is a /api resource that will be mapped to. in other words,
        // if the cloudfront path matches example.com/api/abc, it will redirect to the
        // /{stage}/api/abc resource of the API
        const apiOriginPath = `/${api.deploymentStage.stageName}`;
        const websiteCloudfront = new Distribution(
            this,
            "SiteDistribution",
            {
                // the default behavior is how we set up the static website
                defaultBehavior: {
                    origin: s3Origin,
                    allowedMethods: AllowedMethods.ALLOW_GET_HEAD_OPTIONS,
                    cachePolicy: CachePolicy.CACHING_OPTIMIZED,
                    viewerProtocolPolicy: ViewerProtocolPolicy.ALLOW_ALL,
                    edgeLambdas: [
                        {
                            functionVersion: authLambda.currentVersion,
                            eventType: LambdaEdgeEventType.VIEWER_REQUEST,
                        }]
                },
                // the addition behaviors is how we set up a reverse proxy to the API
                additionalBehaviors: {
                    "api/*": {
                        origin: new HttpOrigin(apiOriginName, {
                            originId: apiOriginName,
                            protocolPolicy: OriginProtocolPolicy.HTTPS_ONLY,
                            httpPort: 80,
                            httpsPort: 443,
                            originPath: apiOriginPath,
                        }),
                        viewerProtocolPolicy: ViewerProtocolPolicy.HTTPS_ONLY,
                        cachePolicy: CachePolicy.CACHING_DISABLED,
                        allowedMethods: AllowedMethods.ALLOW_ALL,
                        originRequestPolicy: OriginRequestPolicy.ALL_VIEWER_EXCEPT_HOST_HEADER,
                    },
                },
                defaultRootObject: "index.html",
                errorResponses: [
                    {
                        httpStatus: 404,
                        responseHttpStatus: 200,
                        responsePagePath: '/index.html'
                    },
                    {
                        httpStatus: 403,
                        responseHttpStatus: 200,
                        responsePagePath: '/index.html'
                    },
                    {
                        httpStatus: 400,
                        responseHttpStatus: 200,
                        responsePagePath: '/index.html'
                    }
                ]
            }
        );

        // CloudFront distribution
        new CfnOutput(this, 'CloudfrontURL', {value: websiteCloudfront.distributionDomainName});
    }
}