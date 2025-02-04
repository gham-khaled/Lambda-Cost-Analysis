import * as cdk from "aws-cdk-lib";
import {Construct} from "constructs";
import * as iam from "aws-cdk-lib/aws-iam";
import * as lambda from "aws-cdk-lib/aws-lambda";
import {Duration} from "aws-cdk-lib";

export class CdnAuthStack extends cdk.Stack {
    public authFunction: lambda.Function;

    constructor(scope: Construct, id: string, props: cdk.StackProps) {
        super(scope, id, props);
        const lambda_role = new iam.Role(this, 'LambdaEdgeAuth', {
            assumedBy: new iam.CompositePrincipal(
                new iam.ServicePrincipal('lambda.amazonaws.com'),
                new iam.ServicePrincipal('edgelambda.amazonaws.com')
            ),
            managedPolicies: [
                iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole')
            ]
        });
        const authParam = new cdk.CfnParameter(this, 'auth', {
            type: 'String',
            default: 'False',
            allowedValues: ['True', 'False'],
            description: 'Enable or disable basic auth',
        });
        if (authParam.valueAsString == "True") {
            const usernameParam = new cdk.CfnParameter(this, 'username', {
                type: 'String',
                description: 'Username for basic auth',
                noEcho: true, // Hide the parameter value in AWS console
            });

            const passwordParam = new cdk.CfnParameter(this, 'password', {
                type: 'String',
                description: 'Password for basic auth',
                noEcho: true, // Hide the parameter value in AWS console
            });
        }


        this.authFunction = new lambda.Function(this, 'cdnAuthFunction', {
            runtime: lambda.Runtime.PYTHON_3_10,
            handler: 'cloudfront.auth.lambda_handler',
            code: lambda.Code.fromAsset('../backend/'),
            role: lambda_role,
            // environment: {
            //     AUTH_ENABLED: authParam.valueAsString,
            //     USERNAME: cdk.Fn.conditionIf(authParam.valueAsString, usernameParam.valueAsString, '').toString(),
            //     PASSWORD: cdk.Fn.conditionIf(authParam.valueAsString, passwordParam.valueAsString, '').toString(),
            // },
            timeout: Duration.seconds(5)
        });
    }
}