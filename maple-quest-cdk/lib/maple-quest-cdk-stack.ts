import * as cdk from "aws-cdk-lib";
import {
  aws_ec2 as ec2,
  aws_ecs as ecs,
  aws_ecs_patterns as ecs_patterns,
  aws_iam as iam,
  aws_logs as logs,
  aws_rds as rds,
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

    // Create RDS secret for Postgres
    const dbCredentialsSecret = new rds.DatabaseSecret(this, "PostgresSecret", {
      username: "postgres",
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

    const dbInstance = new rds.DatabaseInstance(this, "MapleQuestRDS", {
      engine: rds.DatabaseInstanceEngine.postgres({
        version: rds.PostgresEngineVersion.VER_17_4,
      }),
      instanceType: ec2.InstanceType.of(
        ec2.InstanceClass.T4G,
        ec2.InstanceSize.MICRO
      ),
      vpc,
      credentials: rds.Credentials.fromSecret(dbCredentialsSecret),
      multiAz: false,
      allocatedStorage: 20,
      storageType: rds.StorageType.GP2,
      publiclyAccessible: true, // allows DBeaver connection
      vpcSubnets: { subnetType: ec2.SubnetType.PUBLIC },
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      deletionProtection: false,
      databaseName: "maplequest",
    });

    dbInstance.connections.allowFromAnyIpv4(
      ec2.Port.tcp(5432),
      "Allow all inbound PostgreSQL traffic"
    );

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
        SECRET_KEY: process.env.SECRET_KEY!,
        DEBUG: process.env.DEBUG ?? "False",
        ALLOWED_HOSTS: process.env.ALLOWED_HOSTS ?? "*",
        USE_HTTPS: process.env.USE_HTTPS ?? "False",
      },
      secrets: {
        DB_NAME: ecs.Secret.fromSecretsManager(dbCredentialsSecret, "dbname"),
        DB_USER: ecs.Secret.fromSecretsManager(dbCredentialsSecret, "username"),
        DB_PASSWORD: ecs.Secret.fromSecretsManager(dbCredentialsSecret, "password"),
        DB_HOST: ecs.Secret.fromSecretsManager(dbCredentialsSecret, "host"),
        DB_PORT: ecs.Secret.fromSecretsManager(dbCredentialsSecret, "port"),
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
        enableExecuteCommand: true,
      }
    );

    dbInstance.connections.allowDefaultPortFrom(fargateService.service);

    new cdk.CfnOutput(this, "ServiceURL", {
      value: `http://${fargateService.loadBalancer.loadBalancerDnsName}`,
    });

    new cdk.CfnOutput(this, "RDS_Endpoint", {
      value: dbInstance.dbInstanceEndpointAddress,
    });

    new cdk.CfnOutput(this, "RDS_Secret_Arn", {
      value: dbCredentialsSecret.secretArn,
    });
  }
}
