#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import {ReportApiStack} from '../lib/report-api-stack';
import {StepFunctionAnalysisStack} from "../lib/step-function-analysis-stack";
import {S3WebsiteStack} from "../lib/s3-website-stack";
import {CdnAuthStack} from "../lib/cdn-auth";

const app = new cdk.App();
const currentDev = {  region: 'us-west-2'  };

const sfAnalysisStack = new StepFunctionAnalysisStack(app, 'StepFunctionAnalysisStack', {env: currentDev});
const reportApiStack = new ReportApiStack(app, 'ReportApiStack', {env: currentDev}, sfAnalysisStack.analysisStepFunction, sfAnalysisStack.analysisBucket);
const cdnAuthStack = new CdnAuthStack(app, 'CdnAuthStack', {env: {  region: 'us-east-1'  }, crossRegionReferences: true});
new S3WebsiteStack(app, 'ReportWebsiteStack', {env: currentDev, crossRegionReferences: true}, reportApiStack.api, cdnAuthStack.authFunction);
