import * as cdk from "aws-cdk-lib";
import {Construct} from "constructs";
import {CfnOutput} from "aws-cdk-lib";
import {
    AllowedMethods,
    CachePolicy,
    Distribution, LambdaEdgeEventType,
    OriginAccessIdentity, OriginProtocolPolicy, OriginRequestPolicy,
    ViewerProtocolPolicy
} from "aws-cdk-lib/aws-cloudfront";
import {HttpOrigin, S3Origin} from "aws-cdk-lib/aws-cloudfront-origins";
import * as apigateway from "aws-cdk-lib/aws-apigateway";
import * as s3 from "aws-cdk-lib/aws-s3";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as ssm from 'aws-cdk-lib/aws-ssm';
import * as iam from 'aws-cdk-lib/aws-iam';
import {CdnAuthStack} from "./cdn-auth";


export interface CdnAuthStackProps extends cdk.StackProps {
    // readonly bucket: s3.Bucket;
    readonly authLambda: lambda.Function;
    readonly api: apigateway.RestApi;
}

export class CdnDistributionStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props: CdnAuthStackProps) {
        super(scope, id, props);

        const s3WebBucketName = ssm.StringParameter.valueForStringParameter(this, '/lambda-cost-analysis/s3WebBucketName')
        const s3WebBucket = s3.Bucket.fromBucketName(this, "s3WebBucket", s3WebBucketName)

        // console.log(`Rest API ID ${restApiID}`)
        const cloudfrontOAI = new OriginAccessIdentity(this, 'cloudfront-OAI',);
        const s3Origin = new S3Origin(s3WebBucket, {originAccessIdentity: cloudfrontOAI})
        const apiOriginName = `${props.api.restApiId}.execute-api.${this.region}.amazonaws.com`;

        const apiOriginPath = `/${props.api.deploymentStage.stageName}`;
        const logBucket = new s3.Bucket(this, "CloudFrontLogsBucket", {
            removalPolicy: cdk.RemovalPolicy.RETAIN,
            objectOwnership: s3.ObjectOwnership.BUCKET_OWNER_PREFERRED, // En
            encryption: s3.BucketEncryption.S3_MANAGED,
        });
        // const apiOriginPath = `/prod`;
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
                            functionVersion: props.authLambda.currentVersion,
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
                ],

                enableLogging: true,
                logBucket: logBucket,
                logIncludesCookies: true,
                logFilePrefix: "lambda-analytics-cf-logs/"

            },
        );

        const policyStatement = new iam.PolicyStatement({
            actions: ['s3:GetObject'],
            resources: [s3WebBucket.arnForObjects("*")],
            principals: [cloudfrontOAI.grantPrincipal],
        });

        const bucketPolicy = new s3.BucketPolicy(this, 'cloudfrontAccessBucketPolicy', {
            bucket: s3WebBucket,
        })
        bucketPolicy.document.addStatements(policyStatement);
        // CloudFront distribution
        new CfnOutput(this, 'CloudfrontURL', {value: websiteCloudfront.distributionDomainName});
        // Output the website URL

    }
}