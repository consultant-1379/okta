import ldap
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User

from pprint import pprint

class LDAPBackend(object):

    def authenticate(self, request, username=None, password=None):
        user = None
        try:
            user = User.objects.get(username=username)
            if (check_credentials(username, password) == False):
                user = None
                return None
                
        except User.DoesNotExist:
            if(check_credentials(username, password)):
                user = User(username=username, password=password)
                try:
                    user.email = getLdapEmail(username, password)[0]
                except Exception as e:
                    print('Could not get user email from LDAP')
                    user.email = None
                user.save()
        finally:
            return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


def check_credentials(username, password):
    LDAP_USERNAME = '%s@ericsson.se' % username
    LDAP_PASSWORD = password
    LDAP_SERVER = 'ldaps://SESSIWEGAD0003.ericsson.se:3269'
    ldap_client = ldap.initialize(LDAP_SERVER)
    try:
        ldap_client.set_option(ldap.OPT_REFERRALS,0) # perform a synchronous bind
        print(LDAP_USERNAME + " " + LDAP_USERNAME)
        ldap_client.simple_bind_s(LDAP_USERNAME, LDAP_PASSWORD)
        return True
    except ldap.INVALID_CREDENTIALS:
        ldap_client.unbind()
        print('Wrong username or password')
        return False
    except ldap.SERVER_DOWN:
        print('LDAP server not available')
        return False

def getLdapEmail(username, password):
    LDAP_USERNAME = '%s@ericsson.se' % username
    LDAP_PASSWORD = password
    LDAP_SERVER = 'ldaps://SESSIWEGAD0003.ericsson.se:3269'

    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
    l = ldap.initialize(LDAP_SERVER)
    try:
        l.simple_bind_s(LDAP_USERNAME, LDAP_PASSWORD)

        baseDN = "dc=ericsson,dc=se"
        searchScope = ldap.SCOPE_SUBTREE
        searchFilter = "(mailNickname=" + username + ")"
        users = {}
        ldap_result_id = l.search(baseDN, searchScope, searchFilter)
        rType, rData = l.result(ldap_result_id, 0)
        return rData[0][1]['mail']
    except:
        return None

