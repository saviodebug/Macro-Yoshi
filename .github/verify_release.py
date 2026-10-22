"""Public download verification only. Does not contain application source or keys."""
import base64
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import urllib.request

REPO = 'saviodebug/Macro-Yoshi'
REPOSITORIES = (REPO, 'saviodebug/yoshi-updates')
KEY = 'DwIcWrpViPskNtooK3lflZYEN7pCVAsDnhwIBVBGh8Y='

def validate_transport_url(target, *, initial=False):
    from urllib.parse import urlsplit
    url = urlsplit(target)
    if url.scheme != 'https' or url.username or url.password or url.port not in (None,443) or url.fragment:
        raise ValueError('Unsafe download URL')
    if target == 'https://api.github.com/repos/'+REPO+'/releases/latest':
        return
    if url.hostname == 'github.com':
        if url.query:
            raise ValueError('Unexpected GitHub download query')
        for repository in REPOSITORIES:
            prefix = '/'+repository+'/releases/'
            if url.path == prefix+'latest/download/latest.json':
                return
            pattern = re.escape(prefix)+r'download/v([0-9]+\.[0-9]+\.[0-9]+)/(?:latest\.json|macro-yoshi-\1\.exe)'
            if re.fullmatch(pattern,url.path):
                return
        raise ValueError('Unexpected GitHub repository or release path')
    if not initial and url.hostname in ('release-assets.githubusercontent.com','objects.githubusercontent.com'):
        if url.path.startswith(('/github-production-release-asset/','/github-production-release-asset-2e65be/')):
            return
    raise ValueError('Unexpected download host or path')

def strict_json(data):
    def pairs(items):
        result = {}
        for key,value in items:
            if key in result:
                raise ValueError('Duplicate JSON key')
            result[key] = value
        return result
    def invalid_constant(value):
        raise ValueError('Invalid JSON constant: '+value)
    return json.loads(data,object_pairs_hook=pairs,parse_constant=invalid_constant)

class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, target):
        validate_transport_url(target)
        return super().redirect_request(request, fp, code, message, headers, target)

def download(url, limit):
    validate_transport_url(url,initial=True)
    opener = urllib.request.build_opener(SafeRedirect())
    request = urllib.request.Request(url, headers={'User-Agent':'YOSHI-release-verifier'})
    with opener.open(request, timeout=90) as response:
        data = response.read(limit+1)
    if len(data)>limit:
        raise ValueError('Download exceeds size limit')
    return data

def validate_envelope(envelope):
    if type(envelope) is not dict or set(envelope) != {'payload','signature'}:
        raise ValueError('Unexpected envelope fields')
    payload = envelope['payload']
    fields = {'schema','product','platform','version','build','min_updater','size','sha256','url','notes','published_at'}
    if type(payload) is not dict or set(payload) != fields:
        raise ValueError('Unexpected manifest fields')
    if type(payload['schema']) is not int or payload['schema'] != 1 or payload['product'] != 'yoshi-macro' or payload['platform'] != 'windows-x64' or type(payload['min_updater']) is not int or payload['min_updater'] != 1:
        raise ValueError('Incompatible updater manifest')
    version = payload['version']
    if type(version) is not str or not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+',version):
        raise ValueError('Invalid version')
    expected = {'https://github.com/'+repository+'/releases/download/v'+version+'/macro-yoshi-'+version+'.exe' for repository in REPOSITORIES}
    if type(payload['url']) is not str or payload['url'] not in expected or type(payload['sha256']) is not str or not re.fullmatch('[0-9a-f]{64}',payload['sha256']):
        raise ValueError('Unexpected package URL/hash')
    if type(payload['build']) is not int or payload['build'] < 1 or type(payload['published_at']) is not int or payload['published_at'] < 1:
        raise ValueError('Invalid build or publication time')
    if type(payload['notes']) is not list or any(type(item) is not str for item in payload['notes']):
        raise ValueError('Invalid release notes')
    if type(payload['size']) is not int or not 1024 <= payload['size'] <= 200*1024*1024:
        raise ValueError('Invalid executable size')
    raw = json.dumps(payload, sort_keys=True, separators=(',',':'), ensure_ascii=True).encode()
    if type(envelope['signature']) is not str:
        raise ValueError('Invalid signature type')
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
    metadata = strict_json(download('https://api.github.com/repos/'+REPO+'/releases/latest',1024*1024))
    envelope = strict_json(download('https://github.com/'+REPO+'/releases/latest/download/latest.json',32768))
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
