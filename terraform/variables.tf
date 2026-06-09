variable "tenancy_ocid" {}
variable "user_ocid" {}
variable "fingerprint" {}
variable "private_key_path" {}
variable "region" {}

variable "compartment_ocid" {
    description = "Compartiment Oracle où créer les ressources"
}

variable "ssh_public_key" {
    description = "Clé SSH publique pour se connecter au serveur"
}