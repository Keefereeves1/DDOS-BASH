import socket
import struct
import time
import threading
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import dh

# Define authorized network bytes (replace this with your 330 authorized bytes)
authorized_bytes = [
       b'\x00' * 30,
    b'\xFF' * 30,
    b'\x55\xAA' * 15,
    b'\x12\x34\x56\x78\x9A\xBC\xDE\xF0\x11\x22\x33\x44\x55\x66\x77\x88\x99\xAA\xBB\xCC\xDD\xEE\xFF\x00\x01\x02\x03\x04\x05\x06\x07',
    b'\x01\x02\x03\x04\x05',
    b'\xAA\xBB\xCC\xDD\xEE',
    b'\xFF\x00\xFF\x00\xFF',
    b'\x10\x20\x30\x40\x50',
    b'\xDE\xAD\xBE\xEF\xCA',
    b'\x55\x55\x55\x55\x55',
    b'\x00\x11\x22\x33\x44',
    b'\x0F\x0F\x0F\x0F\x0F',
    b'\x99\x88\x77\x66\x55',
    b'\xBB\xAA\x99\x88\x77',
    b'\xCC\xDD\xEE\xFF\x00',
    b'\x12\x34\x56\x78\x9A',
    b'\xFE\xDC\xBA\x98\x76',
    b'\x9F\x9F\x9F\x9F\x9F',
    b'\x55\xAA\x55\xAA\x55',
    b'\xBB\xBB\xBB\xBB\xBB',
    b'\xCC\xCC\xCC\xCC\xCC',
    b'\xDD\xDD\xDD\xDD\xDD',
    b'\xEE\xEE\xEE\xEE\xEE',
    b'\xFF\xFF\xFF\xFF\xFF',
    b'\x01\x02\x03\x04\x05',
    b'\xAA\xBB\xCC\xDD\xEE',
    b'\xFF\x00\xFF\x00\xFF',
    b'\x10\x20\x30\x40\x50',
    b'\xDE\xAD\xBE\xEF\xCA',
    b'\x55\x55\x55\x55\x55',
    b'\x00\x11\x22\x33\x44',
    b'\x0F\x0F\x0F\x0F\x0F',
    b'\x99\x88\x77\x66\x55',
    b'\xBB\xAA\x99\x88\x77',
     b'\x11\x22\x33\x44\x55',
    b'\x66\x77\x88\x99\xAA',
    b'\xBB\xCC\xDD\xEE\xFF',
    b'\xFE\xDC\xBA\x98\x76',
    b'\x9F\x8E\x7D\x6C\x5B',
    b'\x4A\x3B\x2C\x1D\x0E',
    b'\x0D\x1E\x2F\x3C\x4B',
    b'\x5A\x69\x78\x87\x96',
    b'\x63\x72\x81\x90\xAF',
    b'\xCA\xB9\xA8\xF7\xE6',
    b'\x05\x14\x23\x32\x41',
    b'\xE1\xF0\x0F\xFE\x2D',
    b'\xC3\xD2\xA1\xB0\x9F',
    b'\x8C\xBD\xAE\x9D\xEC',
    b'\x2B\x1A\x69\x78\x57',
    b'\x46\x35\x24\x13\xC2',
    b'\x74\x63\x52\x41\xF0',
    b'\xD6\xC5\xB4\xA3\x92',
    b'\x81\x70\x6F\x5E\x4D',
    b'\xF1\xE0\xDF\xCE\xBD',
    b'\xA9\xB8\x87\x96\xD5',
    b'\x25\x34\x03\x12\xA1',
    b'\x1E\x0D\xFC\xEB\xDA',
    b'\x07\x16\x25\x34\x43',
    b'\x39\x28\x17\x06\x55',
    b'\x48\x67\x56\x45\x24',
    b'\x70\x5F\x4E\x3D\x1C',
    b'\x9A\x8B\xFA\xE9\xD8',
    b'\xB7\xA6\x95\x84\x73'
]

# Network interface and ports
interface = "eth0"
listening_port = 8080

# AES encryption settings
encryption_key = b'secret_key'  # Replace with your own key

# DDoS detection settings
threshold = 1000  # Threshold for incoming packets per second
detection_interval = 1  # Detection interval in seconds

# Global variables for packet count
packet_count = 0
last_detection_time = time.time()

# Function to encrypt packet payload
def encrypt_packet(payload, key):
    # Create an AES cipher with the provided key and ECB mode
    cipher = Cipher(algorithms.AES(key), modes.ECB())

    # Create a encryptor object
    encryptor = cipher.encryptor()

    # Add padding to payload if needed
    padder = padding.PKCS7(128).padder()
    padded_payload = padder.update(payload) + padder.finalize()

    # Encrypt the payload
    encrypted_payload = encryptor.update(padded_payload) + encryptor.finalize()
    
    return encrypted_payload

# Function to handle incoming packets
def handle_packet(packet):
    global packet_count, last_detection_time

    # Check if the packet matches any authorized bytes
    if packet in authorized_bytes:
        print("Authorized network access detected.")
    else:
        # Increment packet count
        packet_count += 1

        # Check for DDoS detection
        current_time = time.time()
        if current_time - last_detection_time >= detection_interval:
            if packet_count >= threshold:
                print(f"Possible DDoS detected: {packet_count} packets in {detection_interval} seconds")
            packet_count = 0
            last_detection_time = current_time

# Function to capture and process packets
def capture_packets():
    with socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0003)) as s:
        s.bind((interface, 0))
        while True:
            packet = s.recv(65565)
            eth_length = 14

            eth_header = packet[:eth_length]
            eth = struct.unpack("!6s6sH", eth_header)
            eth_protocol = socket.ntohs(eth[2])

            if eth_protocol == 8:  # IPv4
                ip_header = packet[eth_length:20 + eth_length]
                iph = struct.unpack('!BBHHHBBH4s4s', ip_header)
                version_ihl = iph[0]
                ihl = version_ihl & 0xF
                iph_length = ihl * 4

                src_ip = socket.inet_ntoa(iph[8])
                dst_ip = socket.inet_ntoa(iph[9])

                tcp_header = packet[eth_length + iph_length:eth_length + iph_length + 20]
                tcph = struct.unpack('!HHLLBBHHH', tcp_header)
                source_port = tcph[0]
                dest_port = tcph[1]

                payload = packet[eth_length + iph_length + tcph[4]*4:]

                # Encrypt payload and handle the packet
                encrypted_payload = encrypt_packet(payload, encryption_key)
                handle_packet(encrypted_payload)

# Start packet capture in a separate thread
capture_thread = threading.Thread(target=capture_packets)
capture_thread.daemon = True
capture_thread.start()

# Main application loop (you can add more functionality here)
if __name__ == "__main__":
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Shutting down...")
