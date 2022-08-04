terraform {
    required_providers {
        scalr = {
            source = "registry.scalr.dev/scalr/scalr"
            version= "1.0.0-rc-develop"
        }
    }
}

variable "account_id" {
  type = string
}

variable "env_name" {
  type = string
  default = "Environment A"
}

variable "vcs_name" {
  type = string
}

variable "organization_name" {
  type = string
}

variable "tags" {
  type = list(string)
  default = ["first-key:first-value"]
}

data "scalr_environment" "demo" {
  account_id = var.account_id
  name = var.env_name
}

data "scalr_vcs_provider" "demo" {
  account_id = var.account_id
  name = var.vcs_name
}

resource "scalr_tag" "example" {
  count = length(var.tags)
  name       = var.tags[count.index]
  account_id = var.account_id
}

module "aws-account-scalr-configuration" {
  source = "github.com/Scalr/terraform-scalr-provider-configuration-aws"

  name = "scalr-managed-aws-account-configuration"
  role_name = "ScalrProviderConfigurationTags"
  scalr_account_id = var.account_id

  # policy permissions are required for the module-created role
  policy_permissions = ["ec2:*"]
}

resource "scalr_workspace" "dynamic-tags" {
  name = "dynamic-tags"
  environment_id = data.scalr_environment.demo.id
  vcs_provider_id = data.scalr_vcs_provider.demo.id
  working_directory = "example"

  vcs_repo {
    identifier = "${var.organization_name}/terraform-scalr-yor"
    branch = "main"
    trigger_prefixes = ["example"]
  }

  hooks {
    pre_plan = "bash ./pre-plan.sh"
  }

  tag_ids = scalr_tag.example.*.id

  provider_configuration {
    id = module.aws-account-scalr-configuration.configuration_id
  }
}