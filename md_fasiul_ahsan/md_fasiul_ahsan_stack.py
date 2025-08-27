
# from aws_cdk import (
#     Stack,
#     aws_lambda as lambda_,
# )
# from constructs import Construct

# class MdFasiulAhsanStack(Stack):
#     def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
#         super().__init__(scope, construct_id, **kwargs)

#         fn = lambda_.Function(
#             self, "HelloLambda",
#             runtime=lambda_.Runtime.PYTHON_3_12,               # 👈 supported runtime
#             handler="HelloWorld.lambda_handler",               # file: HelloWorld.py, func: lambda_handler
#             code=lambda_.Code.from_asset("md_fasiul_ahsan/modules"),  # 👈 correct folder
#         )


from aws_cdk import (
    Stack, Duration,
    aws_lambda as _lambda,
    aws_events as events,
    aws_events_targets as targets,
    aws_cloudwatch as cloudwatch,
    aws_iam as iam,
    CfnOutput,
)
from constructs import Construct

class MdFasiulAhsanStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # --- Lambda canary ---
        canary = _lambda.Function(
            self, "WebCanary",
            runtime=_lambda.Runtime.PYTHON_3_12,           # supported runtime
            handler="canary.handler",                      # file canary.py, func handler
            code=_lambda.Code.from_asset("md_fasiul_ahsan/modules"),
            timeout=Duration.seconds(30),
            environment={
            "TARGET_URL": "https://medilinks.com.au/",
            "NAMESPACE": "Canary",
            "SITE_NAME": "Medilinks"   # this becomes a CloudWatch dimension
        },
        )

        # Allow Lambda to publish custom metrics
        canary.add_to_role_policy(iam.PolicyStatement(
            actions=["cloudwatch:PutMetricData"],
            resources=["*"]
        ))

        # --- Schedule: run every 5 minutes ---
        rule = events.Rule(
            self, "CanarySchedule",
            schedule=events.Schedule.rate(Duration.minutes(5))
        )
        rule.add_target(targets.LambdaFunction(canary))

        # --- Alarms on metrics the function will emit ---
        availability_metric = cloudwatch.Metric(
            namespace="Canary", metric_name="Availability",
            period=Duration.minutes(5), statistic="Average"
        )
        latency_metric = cloudwatch.Metric(
            namespace="Canary", metric_name="LatencyMs",
            period=Duration.minutes(5), statistic="Average"
        )

        cloudwatch.Alarm(
            self, "AvailabilityAlarm",
            metric=availability_metric,
            threshold=0.5,                                   # < 1 means a failure
            comparison_operator=cloudwatch.ComparisonOperator.LESS_THAN_THRESHOLD,
            evaluation_periods=1, datapoints_to_alarm=1
        )
        cloudwatch.Alarm(
            self, "LatencyAlarm",
            metric=latency_metric,
            threshold=2000,                                  # ms; adjust as needed
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            evaluation_periods=1, datapoints_to_alarm=1
        )

        CfnOutput(self, "FunctionName", value=canary.function_name)
        CfnOutput(self, "Schedule", value=rule.rule_name)


# from aws_cdk import (
#     Stack, Duration,
#     aws_lambda as _lambda,
#     aws_events as events,
#     aws_events_targets as targets,
#     aws_cloudwatch as cloudwatch,
#     aws_iam as iam,
#     CfnOutput,
# )
# from constructs import Construct

# class MdFasiulAhsanStack(Stack):
#     def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
#         super().__init__(scope, construct_id, **kwargs)

#         # --- Lambda canary (single function, checks a list from sites.json) ---
#         canary = _lambda.Function(
#             self, "WebCanary",
#             runtime=_lambda.Runtime.PYTHON_3_12,
#             handler="canary.handler",
#             code=_lambda.Code.from_asset("md_fasiul_ahsan/modules"),  # includes sites.json
#             timeout=Duration.seconds(30),
#             environment={
#                 "NAMESPACE": "Canary",
#                 "TIMEOUT_SECONDS": "10",   # optional HTTP timeout
#             },
#         )

#         # Allow Lambda to publish custom metrics
#         canary.add_to_role_policy(iam.PolicyStatement(
#             actions=["cloudwatch:PutMetricData"],
#             resources=["*"],
#         ))

#         # --- Schedule: run every 5 minutes ---
#         rule = events.Rule(
#             self, "CanarySchedule",
#             schedule=events.Schedule.rate(Duration.minutes(5)),
#         )
#         rule.add_target(targets.LambdaFunction(canary))

#         # --- (Optional) Alarms PER SITE (because metrics are dimensioned by SiteName) ---
#         sites = ["Medilinks", "SkipQ", "LeetCode"]   # must match names in sites.json

#         for site in sites:
#             availability_metric = cloudwatch.Metric(
#                 namespace="Canary",
#                 metric_name="Availability",
#                 dimensions_map={"SiteName": site},
#                 period=Duration.minutes(5),
#                 statistic="Average",
#             )
#             latency_metric = cloudwatch.Metric(
#                 namespace="Canary",
#                 metric_name="LatencyMs",
#                 dimensions_map={"SiteName": site},
#                 period=Duration.minutes(5),
#                 statistic="p95",  # or "Average"
#             )

#             cloudwatch.Alarm(
#                 self, f"{site}AvailabilityAlarm",
#                 metric=availability_metric,
#                 threshold=1.0,  # any failure in the 5-min period triggers
#                 comparison_operator=cloudwatch.ComparisonOperator.LESS_THAN_THRESHOLD,
#                 evaluation_periods=1,
#                 datapoints_to_alarm=1,
#             )

#             cloudwatch.Alarm(
#                 self, f"{site}LatencyAlarm",
#                 metric=latency_metric,
#                 threshold=2000,  # ms; tune for your SLO
#                 comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
#                 evaluation_periods=1,
#                 datapoints_to_alarm=1,
#             )

#         CfnOutput(self, "FunctionName", value=canary.function_name)
#         CfnOutput(self, "Schedule", value=rule.rule_name)
