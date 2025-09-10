from aws_cdk import (
    Stack, Duration, RemovalPolicy,
    aws_lambda as _lambda,
    aws_events as events,
    aws_events_targets as targets,
    aws_cloudwatch as cloudwatch,
    aws_iam as iam,
    aws_dynamodb as dynamodb,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_cloudwatch_actions as actions,
    CfnOutput,
)
from constructs import Construct


class MdFasiulAhsanStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ---------- DynamoDB table (stores results per site & time) ----------
        # PK = SiteName, SK = PingTime (you'll write these from canary.py)
        table = dynamodb.Table(
            self, "CanaryResults",
            partition_key=dynamodb.Attribute(name="SiteName", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="PingTime", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,   # clean up on cdk destroy (use RETAIN in prod)
            time_to_live_attribute="TtlEpoch",      # optional; only used if you set it in canary.py
        )

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
                "TABLE_NAME": table.table_name,                    # <-- for DynamoDB writes
            },
        )

        # Allow publishing custom metrics
        canary.add_to_role_policy(iam.PolicyStatement(
            actions=["cloudwatch:PutMetricData"],
            resources=["*"],
        ))

        # Allow Lambda to write to the table
        table.grant_write_data(canary)

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

        # ---------- SNS topic + email subscription for notifications ----------
        topic = sns.Topic(self, "CanaryAlerts", display_name="Canary Alerts")
        topic.add_subscription(subs.EmailSubscription("fasiulahsan1997@gmail.com"))  # <-- change this

        # Wire all alarms to SNS (both ALARM and OK)
        for a in latency_alarms + availability_alarms:
            a.add_alarm_action(actions.SnsAction(topic))
            a.add_ok_action(actions.SnsAction(topic))

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
        CfnOutput(self, "TableName", value=table.table_name)
        CfnOutput(self, "SnsTopicArn", value=topic.topic_arn)
