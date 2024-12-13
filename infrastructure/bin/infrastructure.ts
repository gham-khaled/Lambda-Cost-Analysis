#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import {ReportApiStack} from '../lib/report-api-stack';
import {StepFunctionAnalysisStack} from "../lib/step-function-analysis-stack";
import {S3WebsiteStack} from "../lib/s3-website-stack";
import {CdnAuthStack} from "../lib/cdn-auth";

const app = new cdk.App();
const envDev = {account: '068008800301', region: 'eu-west-1', profile: 'sinda',  crossRegionReferences: true}
// const envShifted = {account: '990090217414', region: 'us-west-2'}
const currentDev = envDev
const currentDevUS = { ...envDev, region: 'us-east-1'  };

const sfAnalysisStack = new StepFunctionAnalysisStack(app, 'StepFunctionAnalysisStack', {env: currentDev});
const cdnAuthStack = new CdnAuthStack(app, 'CdnAuthStack', {env: currentDevUS, crossRegionReferences: true});
const reportApiStack = new ReportApiStack(app, 'ReportApiStack', {env: currentDev}, sfAnalysisStack.analysisStepFunction, sfAnalysisStack.analysisBucket);
new S3WebsiteStack(app, 'ReportWebsiteStack', {env: currentDev, crossRegionReferences: true}, reportApiStack.api, cdnAuthStack.authFunction);
