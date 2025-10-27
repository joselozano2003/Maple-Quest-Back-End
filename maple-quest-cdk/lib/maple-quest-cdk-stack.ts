import * as cdk from "aws-cdk-lib";
import {
  aws_ec2 as ec2,
  aws_ecs as ecs,
  aws_ecs_patterns as ecs_patterns,
  aws_iam as iam,
  aws_logs as logs,
} from "aws-cdk-lib";
import { Construct } from "constructs";
import * as dotenv from "dotenv";
import * as path from "path";

dotenv.config({ path: path.resolve(__dirname, "../.env.production") });

export class MapleQuestStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const vpc = new ec2.Vpc(this, "Vpc", {
      maxAzs: 2,
    });

    const cluster = new ecs.Cluster(this, "MapleQuestCluster", {
      vpc,
      clusterName: "maple-quest-cluster",
    });

    const executionRole = iam.Role.fromRoleArn(
      this,
      "TaskExecutionRole",
      "arn:aws:iam::508426719460:role/ecsTaskExecutionRole"
    );

    const logGroup = new logs.LogGroup(this, "MapleQuestLogs", {
      logGroupName: "/ecs/maple-quest-new",
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    const taskDef = new ecs.FargateTaskDefinition(this, "TaskDef", {
      cpu: 512,
      memoryLimitMiB: 1024,
      executionRole,
      family: "maple-quest-task",
      runtimePlatform: {
        cpuArchitecture: ecs.CpuArchitecture.X86_64,
        operatingSystemFamily: ecs.OperatingSystemFamily.LINUX,
      },
    });

    const container = taskDef.addContainer("DjangoAppContainer", {
      containerName: "django-app",
      image: ecs.ContainerImage.fromRegistry(
        "508426719460.dkr.ecr.us-west-2.amazonaws.com/maple-quest:latest"
      ),
      logging: ecs.LogDriver.awsLogs({
        logGroup,
        streamPrefix: "django",
      }),
      environment: {
        DB_NAME: process.env.DB_NAME!,
        DB_USER: process.env.DB_USER!,
        DB_PASSWORD: process.env.DB_PASSWORD!,
        DB_HOST: process.env.DB_HOST!,
        DB_PORT: process.env.DB_PORT!,
        SECRET_KEY: process.env.SECRET_KEY!,
        DEBUG: process.env.DEBUG ?? "False",
        ALLOWED_HOSTS: process.env.ALLOWED_HOSTS ?? "*",
        USE_HTTPS: process.env.USE_HTTPS ?? "False"
      },
    });

    container.addPortMappings({
      containerPort: 8000,
      name: "django-app-8000-tcp",
    });

    const fargateService = new ecs_patterns.ApplicationLoadBalancedFargateService(
      this,
      "MapleQuestService",
      {
        cluster,
        taskDefinition: taskDef,
        desiredCount: 1,
        publicLoadBalancer: true,
        assignPublicIp: true,
        listenerPort: 80,
      }
    );

    new cdk.CfnOutput(this, "ServiceURL", {
      value: `http://${fargateService.loadBalancer.loadBalancerDnsName}`,
    });
  }
}
