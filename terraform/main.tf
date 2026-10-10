
terraform {
  required_providers {
    kind = {
      source  = "tehcyx/kind"
      version = "0.6.0"
    }
  }
}

provider "kind" {}

resource "kind_cluster" "default" {
  name           = "adb-devops"
  node_image     = "kindest/node:v1.32.0"
  wait_for_ready = true
}

