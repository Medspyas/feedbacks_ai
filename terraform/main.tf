terraform {
    required_providers {
        oci = {
            source = "oracle/oci"
            version = "~> 5.0"
        }
    }
}

provider "oci" {
    tenancy_ocid     = var.tenancy_ocid
    user_ocid        = var.user_ocid
    fingerprint      = var.fingerprint
    private_key_path = var.private_key_path
    region           = var.region
}


resource "oci_core_vcn" "feedback_vcn" {
    compartment_id = var.compartment_ocid
    cidr_block      = "10.0.0.0/16"
    display_name    = "feedback-ai-vcn"
}


resource "oci_core_subnet" "feedback_subnet" {
    compartment_id   = var.compartment_ocid
    vcn_id            = oci_core_vcn.feedback_vcn.id
    cidr_block        = "10.0.1.0/24"
    display_name      = "feedback-ai-subnet"
    route_table_id    = oci_core_route_table.feedback_rt.id 
    security_list_ids = [oci_core_security_list.feedback_sl.id]
}

resource "oci_core_internet_gateway" "feedback_igw" {
    compartment_id = var.compartment_ocid
    vcn_id          = oci_core_vcn.feedback_vcn.id
    display_name    = "feedback-ai-igw"
    enabled          = true

    
}

resource "oci_core_route_table" "feedback_rt" {
    compartment_id = var.compartment_ocid
    vcn_id          = oci_core_vcn.feedback_vcn.id
    display_name    = "feedback-ai-rt"

    route_rules {
        destination       = "0.0.0.0/0"
        network_entity_id = oci_core_internet_gateway.feedback_igw.id
    } 
}

resource "oci_core_security_list" "feedback_sl" {
    compartment_id = var.compartment_ocid
    vcn_id          = oci_core_vcn.feedback_vcn.id
    display_name    = "feedback-ai-sl"

    egress_security_rules {
        destination = "0.0.0.0/0"
        protocol    = "all"
    }

    ingress_security_rules {
        protocol = "6"
        source   = "0.0.0.0/0"
        tcp_options {
            min = 22
            max = 22
        }
    }

    ingress_security_rules {
        protocol = "6"
        source   = "0.0.0.0/0"
        tcp_options {
            min = 80
            max = 80
        }
    }

    ingress_security_rules {
        protocol = "6"
        source   = "0.0.0.0/0"
        tcp_options {
            min = 443
            max = 443
        }
    }

    ingress_security_rules {
        protocol = "6"
        source   = "0.0.0.0/0"
        tcp_options {
            min = 8000
            max = 8000
        }
    }
}

resource "oci_core_instance" "feedback_server" {
  compartment_id      = var.compartment_ocid
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  display_name        = "feedback-ai-server"
  shape               = "VM.Standard.E2.1.Micro"

 

  source_details {
    source_type = "image"
    source_id   = data.oci_core_images.ubuntu.images[0].id
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.feedback_subnet.id
    assign_public_ip = true
  }

  metadata = {
    ssh_authorized_keys = var.ssh_public_key
    user_data = base64encode(<<-EOF
      #!/bin/bash
      apt-get update
      apt-get install -y docker.io docker-compose
      systemctl start docker
      systemctl enable docker
    EOF
    )
  }
}

data "oci_core_images" "ubuntu" {
    compartment_id          = var.compartment_ocid
    operating_system         = "Canonical Ubuntu"
    operating_system_version = "22.04"
    shape                    = "VM.Standard.E2.1.Micro"
    sort_by                  = "TIMECREATED"
    sort_order               = "DESC"
}

data "oci_identity_availability_domains" "ads" {
    compartment_id = var.tenancy_ocid
}



