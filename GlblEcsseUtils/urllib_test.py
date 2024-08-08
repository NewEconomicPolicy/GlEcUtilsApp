

import urllib

username = 'vdbuser'
password = 'V3r1fy'

# create a password manager
# =========================
password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()

# Add the username and password.
# If we knew the realm, we could use it instead of None
# =====================================================
top_level_url = "https://verifydb.lsce.ipsl.fr/thredds/catalog/verify/VERIFY_INPUT/NITROGEN"
password_mgr.add_password(None, top_level_url, username, password)

handler = urllib.request.HTTPBasicAuthHandler(password_mgr)

# create "opener" (OpenerDirector instance)
opener = urllib.request.build_opener(handler)

# use the opener to fetch a URL
opener.open(a_url)

# Install the opener.
# Now all calls to urllib.request.urlopen use our opener.
urllib.request.install_opener(opener)
