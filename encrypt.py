import bcrypt
import hashlib
import os

salt = os.environ.get('userImportSalt')

def createEncryptedValue(value):
    md5Hash = hashlib.md5(str(value).encode('utf-8')).hexdigest()
    return bcrypt.hashpw(md5Hash.encode('utf-8'), salt.encode('utf-8')).decode("utf-8")