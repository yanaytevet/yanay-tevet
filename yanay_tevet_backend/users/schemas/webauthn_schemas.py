from typing import TypedDict

from ninja import Schema


class RegistrationOptionsSchema(Schema):
    challenge: str
    rp: dict
    user: dict
    pubKeyCredParams: list[dict]
    timeout: int | None = None
    attestation: str | None = None
    authenticatorSelection: dict | None = None
    excludeCredentials: list[dict] | None = None


class LoginOptionsSchema(Schema):
    challenge: str
    rpId: str | None = None
    timeout: int | None = None
    allowCredentials: list[dict] = []
    userVerification: str | None = None


class AttestationResponseInput(Schema):
    clientDataJSON: str
    attestationObject: str
    transports: list[str] | None = None


class RegistrationVerifyInput(Schema):
    id: str
    rawId: str
    type: str
    response: AttestationResponseInput


class AssertionResponseInput(Schema):
    clientDataJSON: str
    authenticatorData: str
    signature: str
    userHandle: str | None = None


class LoginVerifyInput(Schema):
    id: str
    rawId: str
    type: str
    response: AssertionResponseInput


class WebAuthnCredentialInfo(Schema):
    id: int
    credential_id: str
    created_at: str


class CredentialsSchema(Schema):
    has_passkey: bool
    credentials: list[WebAuthnCredentialInfo]


class DeleteCredentialInput(Schema):
    credential_id: str


class DeleteCredentialOutput(Schema):
    success: bool


class ClientDataType(TypedDict):
    type: str
    challenge: str
    origin: str
