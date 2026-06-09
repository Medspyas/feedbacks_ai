output "server_public_ip" {
    description = "IP publique"
    value       = oci_core_instance.feedback_server.public_ip
}