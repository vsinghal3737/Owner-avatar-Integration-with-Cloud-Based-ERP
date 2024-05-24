from flask import Flask, redirect, request, jsonify

from src import config
from src import auth
from intuitlib.enums import Scopes

from src.bus_logic.accounts import AccountAPI
app = Flask(__name__)
account_api = AccountAPI(config.BASE_URL)
@app.route('/authorize')
def authorize():
    auth_url = auth.get_auth_url([Scopes.ACCOUNTING])
    return redirect(auth_url)


@app.route('/redirect')
def oauth_redirect():
    auth_code = request.args.get('code')
    realm_id = request.args.get('realmId')
    state = request.args.get('state')

    if not auth_code:
        return "Authorization code not found in callback URL.", 400

    # Exchange the authorization code for tokens
    tokens = auth.get_tokens(auth_code, realm_id)
    return jsonify(tokens)


# Token Management Endpoints
@app.route('/refresh_token', methods=['POST'])
def refresh_token_route():
    refresh_token_value = request.json.get('refresh_token')

    tokens = auth.refresh_token(refresh_token_value)
    return jsonify(tokens)


@app.route('/revoke_token', methods=['POST'])
def revoke_token_route():
    token = request.json.get('token')

    revoke_response = auth.revoke_token(token)
    return jsonify(revoke_response)


# Account Endpoints
@app.route('/accounts', methods=['GET'])
def get_accounts():
    access_token = request.args.get('access_token')
    realm_id = request.args.get('realm_id')

    accounts_data = account_api.get_all_accounts(access_token, realm_id)
    return jsonify(accounts_data)


@app.route('/accounts/<account_id>', methods=['GET'])
def get_account_by_id(account_id):
    access_token = request.args.get('access_token')
    realm_id = request.args.get('realm_id')

    account_data = account_api.get_account_by_id(account_id, access_token, realm_id)
    return jsonify(account_data)


@app.route('/accounts/<account_id>', methods=['POST'])
def update_account(account_id):
    access_token = request.json.get('access_token')
    realm_id = request.json.get('realm_id')
    update_fields = request.json.get('update_fields')

    updated_account = account_api.update_account(account_id, update_fields, access_token, realm_id)
    return jsonify(updated_account)

