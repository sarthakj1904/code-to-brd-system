#!/usr/bin/env python3
"""
CDK App for Code-to-BRD System
Deploys the complete infrastructure for the AI-powered code analysis system
"""

import aws_cdk as cdk
from code_to_brd_stack import CodeToBrdStack

app = cdk.App()

# Main stack
CodeToBrdStack(
    app, 
    "CodeToBrdStack",
    description="Infrastructure for Code-to-BRD AI Agent System",
    env=cdk.Environment(
        account=app.node.try_get_context("account"),
        region=app.node.try_get_context("region") or "us-east-1"
    )
)

app.synth()
