#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import {ReportApiStack} from '../lib/report-api-stack';
import {StepFunctionAnalysisStack} from "../lib/step-function-analysis-stack";
import {S3WebsiteStack} from "../lib/s3-website-stack";
import {CdnAuthStack} from "../lib/cdn-auth";
import {CdnDistributionStack} from "../lib/cdn-distribution";

const app = new cdk.App();
const authEnabled = app.node.tryGetContext("auth") === "true";  // Ensure it's a boolean
const currentEnv = {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
}

const sfAnalysisStack = new StepFunctionAnalysisStack(app, 'StepFunctionAnalysisStack', {env: currentEnv});
const reportApiStack = new ReportApiStack(app, 'ReportApiStack', {
    analysisStepFunction: sfAnalysisStack.analysisStepFunction,
    env: currentEnv,
    analysisBucket: sfAnalysisStack.analysisBucket
});

const s3WebsiteStack = new S3WebsiteStack(app, 'ReportWebsiteStack', {
    api: reportApiStack.api,
    authEnabled: authEnabled,
    env: currentEnv,
});


if (authEnabled) {
    const cdnAuthStack = new CdnAuthStack(app, 'CdnAuthStack', {
        env: {region: 'us-east-1', account: process.env.CDK_DEFAULT_ACCOUNT}, crossRegionReferences: true // <-- Enable cross region references
    });
    const cdnDistribution = new CdnDistributionStack(app, 'CdnDistributionStack', {
        authLambda: cdnAuthStack.authFunction,
        env: currentEnv,
        crossRegionReferences: true ,// <-- Enable cross region references
        api: reportApiStack.api
    },)
    cdnDistribution.addDependency(s3WebsiteStack)

}
