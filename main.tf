terraform {
    required_providers {
        scalr = {
            source = "registry.scalr.io/scalr/scalr"
            version= "2.5.0"
        }
    }
}

variable "account_id" {
  type = string
}

variable "env_name" {
  type = string
  default = "Environment-A"
}

variable "vcs_name" {
  type = string
}

variable "organization_name" {
  type = string
}

variable "tag_count" {
  sensitive = false
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
  count = var.tag_count
  name = "tag-${count.index}"
  account_id = var.account_id
}

resource "scalr_workspace" "dynamic-tags" {
  name = "dynamic-tags"
  environment_id = data.scalr_environment.demo.id
  vcs_provider_id = data.scalr_vcs_provider.demo.id
  working_directory = "example"

  vcs_repo {
    identifier = "${var.organization_name}/Hook-terraform-scalr-yor"
    branch = "main"
    trigger_prefixes = ["example"]
  }

  hooks {
    pre_plan = "bash ./pre-plan.sh"
  }

   tag_ids = scalr_tag.example[*].id
}

resource "scalr_variable" "delimiter" {
  key = "TAG_DELIMITER"
  value = "_"
  workspace_id = scalr_workspace.dynamic-tags.id
  category = "shell"
}
