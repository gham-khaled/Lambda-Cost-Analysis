#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import {ReportApiStack} from '../lib/report-api-stack';
import {StepFunctionAnalysisStack} from "../lib/step-function-analysis-stack";
import {S3WebsiteStack} from "../lib/s3-website-stack";

const app = new cdk.App();
// const envDev = {account: '068008800301', region: 'eu-west-1'}
const envShifted = {account: '990090217414', region: 'us-west-2'}
const sfAnalysisStack = new StepFunctionAnalysisStack(app, 'StepFunctionAnalysisStack', {env: envShifted});
const reportApiStack = new ReportApiStack(app, 'ReportApiStack', {env: envShifted}, sfAnalysisStack.analysisStepFunction, sfAnalysisStack.analysisBucket);
new S3WebsiteStack(app, 'ReportWebsiteStack', {env: envShifted}, reportApiStack.api);
