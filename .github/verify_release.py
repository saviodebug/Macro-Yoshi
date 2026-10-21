"""Public download verification only. Does not contain application source or keys."""
import base64
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import urllib.request

REPO = 'saviodebug/yoshi-updates'
KEY = 'DwIcWrpViPskNtooK3lflZYEN7pCVAsDnhwIBVBGh8Y='

class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, target):
        from urllib.parse import urlsplit
        url = urlsplit(target)
        if url.scheme != 'https' or url.username or url.password or url.port not in (None,443):
            raise ValueError('Unsafe redirect')
        if url.hostname == 'github.com':
            if not url.path.startswith('/'+REPO+'/releases/'):
                raise ValueError('Unexpected GitHub repository')
        elif url.hostname not in ('release-assets.githubusercontent.com', 'objects.githubusercontent.com'):
            raise ValueError('Unexpected download host')
        return super().redirect_request(request, fp, code, message, headers, target)

def download(url, limit):
    opener = urllib.request.build_opener(SafeRedirect())
    request = urllib.request.Request(url, headers={'User-Agent':'YOSHI-release-verifier'})
    with opener.open(request, timeout=90) as response:
        data = response.read(limit+1)
    if len(data)>limit:
        raise ValueError('Download exceeds size limit')
    return data

def validate_envelope(envelope):
    payload = envelope['payload']
    if set(envelope) != {'payload','signature'}:
        raise ValueError('Unexpected envelope fields')
    if payload['schema'] != 1 or payload['product'] != 'yoshi-macro' or payload['platform'] != 'windows-x64' or payload['min_updater'] != 1:
        raise ValueError('Incompatible updater manifest')
    version = payload['version']
    if not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+',version):
        raise ValueError('Invalid version')
    expected = 'https://github.com/'+REPO+'/releases/download/v'+version+'/macro-yoshi-'+version+'.exe'
    if payload['url'] != expected or not re.fullmatch('[0-9a-f]{64}',payload['sha256']):
        raise ValueError('Unexpected package URL/hash')
    if type(payload['size']) is not int or not 1024 <= payload['size'] <= 200*1024*1024:
        raise ValueError('Invalid executable size')
    raw = json.dumps(payload, sort_keys=True, separators=(',',':'), ensure_ascii=True).encode()
    signature = base64.b64decode(envelope['signature'], validate=True)
    if len(signature) != 64:
        raise ValueError('Invalid signature length')
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        # RFC 8410 SubjectPublicKeyInfo for Ed25519. Public key only.
        (root/'key.der').write_bytes(bytes.fromhex('302a300506032b6570032100')+base64.b64decode(KEY))
        (root/'payload').write_bytes(raw)
        (root/'signature').write_bytes(signature)
        subprocess.run(['openssl','pkeyutl','-verify','-pubin','-keyform','DER','-inkey',str(root/'key.der'),'-rawin','-in',str(root/'payload'),'-sigfile',str(root/'signature')],check=True,capture_output=True)
    return payload

def main():
    metadata = json.loads(download('https://api.github.com/repos/'+REPO+'/releases/latest',1024*1024))
    envelope = json.loads(download('https://github.com/'+REPO+'/releases/latest/download/latest.json',32768))
    payload = validate_envelope(envelope)
    if metadata['tag_name'] != 'v'+payload['version'] or metadata['draft'] or metadata['prerelease']:
        raise ValueError('Release and manifest disagree')
    names = {item['name'] for item in metadata['assets']}
    if names != {'latest.json','macro-yoshi-'+payload['version']+'.exe'} or len(metadata['assets']) != 2:
        raise ValueError('Unexpected public release assets')
    binary = download(payload['url'],payload['size'])
    if len(binary)!=payload['size'] or hashlib.sha256(binary).hexdigest()!=payload['sha256'] or binary[:2]!=b'MZ':
        raise ValueError('Executable integrity failed')
    print('Verified official release '+payload['version']+': Ed25519, SHA-256, size, updater schema and asset allowlist. Executable not executed.')

if __name__ == '__main__':
    main()
