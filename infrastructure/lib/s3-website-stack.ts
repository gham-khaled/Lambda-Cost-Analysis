import * as cdk from "aws-cdk-lib";
import {Construct} from "constructs";
import * as s3 from "aws-cdk-lib/aws-s3";
import {BucketDeployment, Source} from "aws-cdk-lib/aws-s3-deployment";
import * as apigateway from "aws-cdk-lib/aws-apigateway";
import * as custom from "aws-cdk-lib/custom-resources";


export interface S3WebsiteStackProps extends cdk.StackProps {
    readonly api: apigateway.RestApi,
    readonly authEnabled: boolean
}

export class S3WebsiteStack extends cdk.Stack {
    public bucket: s3.Bucket;

    constructor(scope: Construct, id: string, props: S3WebsiteStackProps) {
        super(scope, id, props);


        this.bucket = new s3.Bucket(this, 'analysis-website', {
            websiteIndexDocument: 'index.html',
            publicReadAccess: !props.authEnabled,
            blockPublicAccess: s3.BlockPublicAccess.BLOCK_ACLS,
            autoDeleteObjects: true,
            removalPolicy: cdk.RemovalPolicy.DESTROY
        });

        const bucketDeployment = new BucketDeployment(this, 'MyDeployment', {
            sources: [Source.asset('../frontend/dist/')],
            destinationBucket: this.bucket,
        });
        bucketDeployment.node.addDependency(this.bucket)
        const urlWithoutTrailingSlash = props.api.url.endsWith("/") ? props.api.url.slice(0, -1) : props.api.url;
        const s3Upload = new custom.AwsCustomResource(this, 'config-env', {
            policy: custom.AwsCustomResourcePolicy.fromSdkCalls({resources: custom.AwsCustomResourcePolicy.ANY_RESOURCE}),
            onUpdate: {
                service: "S3",
                action: "putObject",
                parameters: {
                    Body: `var PROD_URL_API = '${urlWithoutTrailingSlash}/api'`,
                    Bucket: this.bucket.bucketName,
                    Key: "env.js",
                },
                physicalResourceId: custom.PhysicalResourceId.of(`config-env-${Date.now()}`)
            }
        });
        s3Upload.node.addDependency(bucketDeployment);
        // new cdk.CfnOutput(this, 'WebsiteURL', {
        //     value: this.bucket.bucketWebsiteUrl,
        // });
    }
}