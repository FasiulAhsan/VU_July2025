# #!/usr/bin/env python3
# import os

# import aws_cdk as cdk

# from md_fasiul_ahsan.md_fasiul_ahsan_stack import MdFasiulAhsanStack


# app = cdk.App()
# MdFasiulAhsanStack(app, "MdFasiulAhsanStack",
#     # If you don't specify 'env', this stack will be environment-agnostic.
#     # Account/Region-dependent features and context lookups will not work,
#     # but a single synthesized template can be deployed anywhere.

#     # Uncomment the next line to specialize this stack for the AWS Account
#     # and Region that are implied by the current CLI configuration.

#     #env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),

#     # Uncomment the next line if you know exactly what Account and Region you
#     # want to deploy the stack to. */

#     #env=cdk.Environment(account='123456789012', region='us-east-1'),

#     # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
#     )

# app.synth()


# #!/usr/bin/env python3
# import os
# import aws_cdk as cdk

# from md_fasiul_ahsan.md_fasiul_ahsan_stack import MdFasiulAhsanStack

# app = cdk.App()

# # Always target your account/region.
# # Uses env vars if present; otherwise falls back to your known values.
# account = os.getenv("CDK_DEFAULT_ACCOUNT", "051859107315")
# region  = os.getenv("CDK_DEFAULT_REGION",  "ap-southeast-2")

# stack = MdFasiulAhsanStack(
#     app,
#     "MdFasiulAhsanStack",
#     env=cdk.Environment(account=account, region=region),
# )

# # (Optional) Helpful tags for billing/visibility
# cdk.Tags.of(stack).add("project", "canary-3url")
# cdk.Tags.of(stack).add("owner", "md-fasiul-ahsan")

# app.synth()


import aws_cdk as cdk
from md_fasiul_ahsan.md_fasiul_ahsan_stack import MdFasiulAhsanStack

app = cdk.App()
MdFasiulAhsanStack(
    app,
    "MdFasiulAhsanStack",
    env=cdk.Environment(account="051859107315", region="ap-southeast-2"),
)
app.synth()
