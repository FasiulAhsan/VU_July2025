# 1st
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


# 2nd

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

#         # --- Lambda canary ---
#         canary = _lambda.Function(
#             self, "WebCanary",
#             runtime=_lambda.Runtime.PYTHON_3_12,           # supported runtime
#             handler="canary.handler",                      # file canary.py, func handler
#             code=_lambda.Code.from_asset("md_fasiul_ahsan/modules"),
#             timeout=Duration.seconds(30),
#             environment={
#             "TARGET_URL": "https://medilinks.com.au/",
#             "NAMESPACE": "Canary",
#             "SITE_NAME": "Medilinks"   # this becomes a CloudWatch dimension
#         },
#         )

#         # Allow Lambda to publish custom metrics
#         canary.add_to_role_policy(iam.PolicyStatement(
#             actions=["cloudwatch:PutMetricData"],
#             resources=["*"]
#         ))

#         # --- Schedule: run every 5 minutes ---
#         rule = events.Rule(
#             self, "CanarySchedule",
#             schedule=events.Schedule.rate(Duration.minutes(5))
#         )
#         rule.add_target(targets.LambdaFunction(canary))

#         # --- Alarms on metrics the function will emit ---
#         availability_metric = cloudwatch.Metric(
#             namespace="Canary", metric_name="Availability",
#             period=Duration.minutes(5), statistic="Average"
#         )
#         latency_metric = cloudwatch.Metric(
#             namespace="Canary", metric_name="LatencyMs",
#             period=Duration.minutes(5), statistic="Average"
#         )

#         cloudwatch.Alarm(
#             self, "AvailabilityAlarm",
#             metric=availability_metric,
#             threshold=0.5,                                   # < 1 means a failure
#             comparison_operator=cloudwatch.ComparisonOperator.LESS_THAN_THRESHOLD,
#             evaluation_periods=1, datapoints_to_alarm=1
#         )
#         cloudwatch.Alarm(
#             self, "LatencyAlarm",
#             metric=latency_metric,
#             threshold=2000,                                  # ms; adjust as needed
#             comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
#             evaluation_periods=1, datapoints_to_alarm=1
#         )

#         CfnOutput(self, "FunctionName", value=canary.function_name)
#         CfnOutput(self, "Schedule", value=rule.rule_name)


#3rd 

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

#         # --- Lambda canary (packages modules/ including sites.json) ---
#         canary = _lambda.Function(
#             self, "WebCanary",
#             runtime=_lambda.Runtime.PYTHON_3_12,
#             handler="canary.handler",                                  # file: canary.py, func: handler
#             code=_lambda.Code.from_asset("md_fasiul_ahsan/modules"),
#             timeout=Duration.seconds(30),
#             environment={
#                 "NAMESPACE": "Canary",
#                 "TIMEOUT_SECONDS": "10",
#             },
#         )

#         # Allow publishing custom metrics
#         canary.add_to_role_policy(iam.PolicyStatement(
#             actions=["cloudwatch:PutMetricData"],
#             resources=["*"],
#         ))

#         # --- Schedule: every 5 minutes ---
#         rule = events.Rule(
#             self, "CanarySchedule",
#             schedule=events.Schedule.rate(Duration.minutes(5)),
#         )
#         rule.add_target(targets.LambdaFunction(canary))

#         # --- Alarms per site (names must match sites.json) ---
#         sites = ["Medilinks", "SkipQ", "LeetCode"]

#         for site in sites:
#             latency_metric = cloudwatch.Metric(
#                 namespace="Canary",
#                 metric_name="LatencyMs",
#                 dimensions_map={"SiteName": site},
#                 period=Duration.minutes(5),
#                 statistic="p95",   # typical for latency
#             )
#             availability_metric = cloudwatch.Metric(
#                 namespace="Canary",
#                 metric_name="Availability",
#                 dimensions_map={"SiteName": site},
#                 period=Duration.minutes(5),
#                 statistic="Average",
#             )

#             # Latency high
#             cloudwatch.Alarm(
#                 self, f"{site}LatencyAlarm",
#                 metric=latency_metric,
#                 threshold=2000,  # ms (tune to your SLO)
#                 comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
#                 evaluation_periods=1,
#                 datapoints_to_alarm=1,
#                 treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
#                 alarm_description=f"{site}: p95 latency > 2000 ms in last 5 minutes",
#             )

#             # Availability below 1 (had at least one failure)
#             cloudwatch.Alarm(
#                 self, f"{site}AvailabilityAlarm",
#                 metric=availability_metric,
#                 threshold=1.0,
#                 comparison_operator=cloudwatch.ComparisonOperator.LESS_THAN_THRESHOLD,
#                 evaluation_periods=1,
#                 datapoints_to_alarm=1,
#                 treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
#                 alarm_description=f"{site}: availability < 1.0 (failure in last 5 minutes)",
#             )

#         CfnOutput(self, "FunctionName", value=canary.function_name)
#         CfnOutput(self, "Schedule", value=rule.rule_name)


# 4th

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

        # ---------- Lambda canary (packages modules/ incl. sites.json) ----------
        canary = _lambda.Function(
            self, "WebCanary",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="canary.handler",                              # file: canary.py, func: handler
            code=_lambda.Code.from_asset("md_fasiul_ahsan/modules"),
            timeout=Duration.seconds(30),
            environment={
                "NAMESPACE": "Canary",
                "TIMEOUT_SECONDS": "10",
            },
        )

        # Allow publishing custom metrics
        canary.add_to_role_policy(iam.PolicyStatement(
            actions=["cloudwatch:PutMetricData"],
            resources=["*"],
        ))

        # ---------- Schedule: every 5 minutes ----------
        rule = events.Rule(
            self, "CanarySchedule",
            schedule=events.Schedule.rate(Duration.minutes(5)),
        )
        rule.add_target(targets.LambdaFunction(canary))

        # ---------- Alarms per site (names must match modules/sites.json) ----------
        sites = ["Medilinks", "SkipQ", "LeetCode"]

        latency_alarms = []
        availability_alarms = []

        for site in sites:
            latency_metric = cloudwatch.Metric(
                namespace="Canary",
                metric_name="LatencyMs",
                dimensions_map={"SiteName": site},
                period=Duration.minutes(5),
                statistic="p95",   # typical for latency
            )
            availability_metric = cloudwatch.Metric(
                namespace="Canary",
                metric_name="Availability",
                dimensions_map={"SiteName": site},
                period=Duration.minutes(5),
                statistic="Average",
            )

            # Latency high
            lat_alarm = cloudwatch.Alarm(
                self, f"{site}LatencyAlarm",
                metric=latency_metric,
                threshold=2000,  # ms (tune to your SLO)
                comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
                evaluation_periods=1,
                datapoints_to_alarm=1,
                treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
                alarm_description=f"{site}: p95 latency > 2000 ms in last 5 minutes",
            )
            latency_alarms.append(lat_alarm)

            # Availability below 1 (had at least one failure)
            avail_alarm = cloudwatch.Alarm(
                self, f"{site}AvailabilityAlarm",
                metric=availability_metric,
                threshold=1.0,
                comparison_operator=cloudwatch.ComparisonOperator.LESS_THAN_THRESHOLD,
                evaluation_periods=1,
                datapoints_to_alarm=1,
                treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
                alarm_description=f"{site}: availability < 1.0 (failure in last 5 minutes)",
            )
            availability_alarms.append(avail_alarm)

        # ---------- Dashboard (graphs + KPIs + alarm status) ----------
        dashboard = cloudwatch.Dashboard(
            self, "CanaryDashboard",
            dashboard_name="3url-canary-dashboard",   # change if you like
        )

        def site_metrics(site: str):
            """Helper: metrics with correct dimensions/stats/period."""
            lat = cloudwatch.Metric(
                namespace="Canary",
                metric_name="LatencyMs",
                dimensions_map={"SiteName": site},
                statistic="p95",
                period=Duration.minutes(5),
            )
            avail = cloudwatch.Metric(
                namespace="Canary",
                metric_name="Availability",
                dimensions_map={"SiteName": site},
                statistic="Average",
                period=Duration.minutes(5),
            )
            return lat, avail

        for site in sites:
            lat, avail = site_metrics(site)

            # Line chart: Latency (left), Availability (right 0..1)
            dashboard.add_widgets(
                cloudwatch.GraphWidget(
                    title=f"{site} – Availability, LatencyMs",
                    left=[lat],
                    right=[avail],
                    left_y_axis=cloudwatch.YAxisProps(label="Latency (ms)"),
                    right_y_axis=cloudwatch.YAxisProps(label="Availability", min=0, max=1),
                    period=Duration.minutes(5),
                    width=24,
                )
            )

            # KPI number tiles
            dashboard.add_widgets(
                cloudwatch.SingleValueWidget(
                    title=f"{site} p95 Latency (ms)",
                    metrics=[lat],
                    width=6,
                ),
                cloudwatch.SingleValueWidget(
                    title=f"{site} Availability (avg)",
                    metrics=[avail],
                    width=6,
                ),
            )

        # Alarm status widget (shows all 6 alarms)
        dashboard.add_widgets(
            cloudwatch.AlarmStatusWidget(
                title="Canary Alarms",
                alarms=latency_alarms + availability_alarms,
                width=24,
            )
        )

        # ---------- Outputs ----------
        CfnOutput(self, "FunctionName", value=canary.function_name)
        CfnOutput(self, "Schedule", value=rule.rule_name)
