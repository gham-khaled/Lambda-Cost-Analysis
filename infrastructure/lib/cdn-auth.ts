import * as cdk from "aws-cdk-lib";
import {Construct} from "constructs";
import * as iam from "aws-cdk-lib/aws-iam";
import * as ssm from 'aws-cdk-lib/aws-ssm';
import * as lambda from "aws-cdk-lib/aws-lambda";
import {Duration} from "aws-cdk-lib";

export class CdnAuthStack extends cdk.Stack {
    public authFunction: lambda.Function;

    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);


        let username = this.node.tryGetContext("username");  // Ensure it's a boolean
        let password = this.node.tryGetContext("password");
        if (username === undefined || password === undefined) {
            throw new Error("❌ Missing required context variable: 'username' or password. Please provide it using --context username=x password=y");
        }
        console.log(`Username: ${username} and Password: ${password}`);

        // Create SSM Parameters
        const usernameParam = new ssm.StringParameter(this, "UsernameParameter", {
            parameterName: "/lambda-cost-analysis/username",
            stringValue: username,
            tier: ssm.ParameterTier.STANDARD,
        });

        const passwordParam = new ssm.StringParameter(this, "PasswordParameter", {
            parameterName: "/lambda-cost-analysis/password",
            stringValue: password,
            tier: ssm.ParameterTier.STANDARD,
        },);


        const lambda_role = new iam.Role(this, 'LambdaEdgeAuth', {
            assumedBy: new iam.CompositePrincipal(
                new iam.ServicePrincipal('lambda.amazonaws.com'),
                new iam.ServicePrincipal('edgelambda.amazonaws.com')
            ),
            managedPolicies: [
                iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole')
            ]
        });



        this.authFunction = new lambda.Function(this, 'cdnAuthFunction', {
            runtime: lambda.Runtime.PYTHON_3_10,
            handler: 'backend.cloudfront.auth.lambda_handler',
            code: lambda.Code.fromAsset('../src/'),
            role: lambda_role,
            timeout: Duration.seconds(5)
        });
        usernameParam.grantRead(this.authFunction);
        passwordParam.grantRead(this.authFunction)
        usernameParam.applyRemovalPolicy(cdk.RemovalPolicy.DESTROY)
        passwordParam.applyRemovalPolicy(cdk.RemovalPolicy.DESTROY)

    }
}
