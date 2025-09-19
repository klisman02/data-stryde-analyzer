STRIDE_CATEGORIES = ['S', 'T', 'R', 'I', 'D', 'E']


DEFAULT_MITIGATIONS = {
'S': ['Use strong authentication (MFA)', 'Harden identity stores'],
'T': ['Input validation', 'Signing and integrity checks'],
'R': ['Audit logs with tamper-evident storage', 'Signed transactions'],
'I': ['Encrypt data at rest and in transit', 'Access controls'],
'D': ['Rate limiting', 'Redundancy and capacity planning'],
'E': ['Principle of least privilege', 'Isolate sensitive processes']
}


def generate_empty_stride():
    return {c: [] for c in STRIDE_CATEGORIES}