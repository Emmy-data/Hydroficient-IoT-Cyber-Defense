import os
import cryptography
import ipaddress
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

def generate_ca_certificate():
    """Generate the Certificate Authority (CA) certificate"""

    # Step 1: Generate a private key for the CA
    ca_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048   # Use 2048 bits for better security while 4096 is used in production
    )

    # Step 2: Define the CA's identity
    ca_name = x509.Name([
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Grand Marina Hotel"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Water Systems Security"),
        x509.NameAttribute(NameOID.COMMON_NAME, "Grand Marina Root CA"),
    ])

    # Step 3: Build and sign the CA certificate
    ca_cert = (
        x509.CertificateBuilder()
        .subject_name(ca_name)
        .issuer_name(ca_name)  # Self-signed: issuer_name equals subject_name
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=3650))
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        )
        .sign(ca_key, hashes.SHA256())
    )
    print("CA certificate generated successfully.")
    return ca_key, ca_cert

# Step 2: Generate the server certificate signed by the CA

def generate_server_certificate(ca_key, ca_cert):
    """Generate the server certificate signed by the CA"""
    server_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    # Define the server's identity
    server_name = x509.Name([
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Grand Marina Hotel"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "MQTT Broker"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"), # Common Name should match the server's hostname 
        #or IP address for TLS to work without warnings
    ])

    server_cert = (
        x509.CertificateBuilder()
        .subject_name(server_name)
        .issuer_name(ca_cert.subject)  # CA is the issuer!
        .public_key(server_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=365))
        .add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
            ]),
            critical=False,
        )
        .add_extension(
            x509.BasicConstraints(ca=False, path_length=None), #Ca is false for server cert
            critical=True,
        )
        .sign(ca_key, hashes.SHA256())  # Signed by CA's key!
    )
    print("Server certificate generated and signed by CA successfully.")
    return server_key, server_cert

## Save the certificates to files for use by the MQTT broker and clients

def save_certificates(ca_cert, server_cert, server_key):
    """Save the CA and server certificates and server key to files"""
    certs_dir = Path("./certs")
    certs_dir.mkdir(exist_ok=True)

    # Save CA certificate
    with open(certs_dir / "ca_cert.pem", "wb") as f:
        f.write(ca_cert.public_bytes(serialization.Encoding.PEM))
    print("CA certificate saved to certs/ca_cert.pem")

    # Save server certificate
    with open(certs_dir / "server_cert.pem", "wb") as f:
        f.write(server_cert.public_bytes(serialization.Encoding.PEM))
    print("Server certificate saved to certs/server_cert.pem")

    # Save server private key (PEM format, unencrypted for simplicity)
    with open(certs_dir / "server_key.pem", "wb") as f:
        f.write(server_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
    print("Server private key saved to certs/server_key.pem")

if __name__ == "__main__":
    ca_key, ca_cert = generate_ca_certificate()
    server_key, server_cert = generate_server_certificate(ca_key, ca_cert)
    save_certificates(ca_cert, server_cert, server_key)
