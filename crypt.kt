import java.io.ByteArrayOutputStream
import java.io.ObjectInputStream
import java.io.ObjectOutputStream

import javax.crypto.Cipher
import javax.crypto.SecretKey
import javax.crypto.SecretKeyFactory
import javax.crypto.spec.IvParameterSpec
import javax.crypto.spec.SecretKeySpec

import kotlinx.serialization.Serializable

object CodingHandshakeEncryption {
    private const val ALGORITHM = "AES/CBC/PKCS5Padding"
    private const val IV_LENGTH = 16

    private fun getCipher(key: String, initializationVector: String): Cipher {
        val keySpec = SecretKeySpec(key.toByteArray(Charsets.US_ASCII), ALGORITHM)
        val iv = initializationVector.toByteArray(Charsets.US_ASCII)
        val cipher = Cipher.getInstance(ALGORITHM)
        cipher.init(Cipher.ENCRYPT_MODE, keySpec)
        cipher.update(iv)
        return cipher
    }

    suspend fun encrypt(message: String, key: String, initializationVector: String): String {
        val cipher = getCipher(key, initializationVector)
        val output = ByteArrayOutputStream()
        val cipherInputStream = CipherInputStream(inputStream(message), cipher)
        cipherInputStream.copyTo(output)
        return Base64.encode(output.toByteArray())
    }

    suspend fun decrypt(message: String, key: String, initializationVector: String): String {
        val cipher = getCipher(key, initializationVector)
        val input = ByteArrayInputStream(Base64.decode(message.toByteArray(Charsets.US_ASCII)))
        suspend fun decrypt(message: String, key: String, initializationVector: String): String {
        val cipher = getCipher(key, initializationVector)
        val input = ByteArrayInputStream(Base64.decode(message.toByteArray(Charsets.US_ASCII)))
        val cipherOutputStream = CipherOutputStream(outputStream(message), cipher)
        input.copyTo(cipherOutputStream)
        return String(cipherOutputStream.toByteArray())
    }

    private fun inputStream(message: String): InputStream = ByteArrayInputStream(message.toByteArray(Charsets.US_ASCII))

    private fun outputStream(message: String): OutputStream = ByteArrayOutputStream()
}

class CodingHandshakeEncryptionTest {
    @Serializable
    data class TestData(val message: String, val key: String, val initializationVector: String)

    fun testEncryption() {
        val testData = TestData("Hello, world!", "mysecretkey", "myinitvector")
        val encryptedMessage = CodingHandshakeEncryption.encrypt(testData.message, testData.key, testData.initializationVector)
        println(encryptedMessage)

        val decryptedMessage = CodingHandshakeEncryption.decrypt(encryptedMessage, testData.key, testData.initializationVector)
        println(decryptedMessage)
    }
}

fun main() {
    val test = CodingHandshakeEncryptionTest()
    test.testEncryption()
}