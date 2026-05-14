import json
from datetime import timedelta

from asgiref.sync import sync_to_async
from django.conf import settings
from django.utils import timezone
from webauthn import (
    generate_authentication_options,
    generate_registration_options,
    options_to_json,
    verify_authentication_response,
    verify_registration_response,
)
from webauthn.helpers import base64url_to_bytes, bytes_to_base64url
from webauthn.helpers.structs import (
    AttestationConveyancePreference,
    AuthenticationCredential,
    AuthenticatorAssertionResponse,
    AuthenticatorAttestationResponse,
    AuthenticatorSelectionCriteria,
    RegistrationCredential,
    ResidentKeyRequirement,
    UserVerificationRequirement,
)

from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from common.time_utils import TimeUtils
from users.models import User
from users.models.webauthn_challenge import WebAuthnChallenge
from users.models.webauthn_credential import WebAuthnCredential
from users.schemas.webauthn_schemas import (
    ClientDataType,
    CredentialsSchema,
    LoginOptionsSchema,
    LoginVerifyInput,
    RegistrationOptionsSchema,
    RegistrationVerifyInput,
    WebAuthnCredentialInfo,
)


class WebAuthnManager:

    MAX_CREDENTIALS = 3

    @classmethod
    async def generate_register_options(cls, user: User) -> RegistrationOptionsSchema:
        credential_count = await WebAuthnCredential.objects.filter(user=user).acount()
        if credential_count >= cls.MAX_CREDENTIALS:
            raise RestAPIException(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                error_code='too_many_passkeys',
                message=f'You cannot register more than {cls.MAX_CREDENTIALS} passkeys',
            )

        options = generate_registration_options(
            rp_id=settings.WEBAUTHN_RP_ID,
            rp_name=settings.WEBAUTHN_RP_NAME,
            user_id=str(user.id).encode(),
            user_name=user.username,
            user_display_name=user.get_full_name() or user.username,
            attestation=AttestationConveyancePreference.NONE,
            authenticator_selection=AuthenticatorSelectionCriteria(
                resident_key=ResidentKeyRequirement.REQUIRED,
                user_verification=UserVerificationRequirement.REQUIRED,
            ),
        )
        await WebAuthnChallenge.objects.acreate(
            challenge=bytes_to_base64url(options.challenge),
            user=user,
            expires_at=timezone.now() + timedelta(seconds=WebAuthnChallenge.CHALLENGE_TTL_SECONDS),
        )
        return RegistrationOptionsSchema(**json.loads(options_to_json(options)))

    @classmethod
    async def verify_registration(cls, user: User, data: RegistrationVerifyInput) -> WebAuthnCredential:
        client_data: ClientDataType = json.loads(
            base64url_to_bytes(data.response.clientDataJSON).decode()
        )
        challenge_value = client_data['challenge']

        challenge_obj = await WebAuthnChallenge.objects.filter(
            challenge=challenge_value,
            user=user,
        ).afirst()

        if not challenge_obj or challenge_obj.is_expired():
            raise RestAPIException(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                error_code='invalid_challenge',
                message='Challenge not found or expired',
            )

        try:
            credential = RegistrationCredential(
                id=data.id,
                raw_id=base64url_to_bytes(data.rawId),
                response=AuthenticatorAttestationResponse(
                    client_data_json=base64url_to_bytes(data.response.clientDataJSON),
                    attestation_object=base64url_to_bytes(data.response.attestationObject),
                    transports=data.response.transports or [],
                ),
            )
            verification = verify_registration_response(
                credential=credential,
                expected_challenge=base64url_to_bytes(challenge_value),
                expected_rp_id=settings.WEBAUTHN_RP_ID,
                expected_origin=settings.WEBAUTHN_ORIGIN,
                require_user_verification=True,
            )
        except Exception as exc:
            raise RestAPIException(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                error_code='verification_failed',
                message=f'Registration verification failed: {exc}',
            )

        await challenge_obj.adelete()

        return await WebAuthnCredential.objects.acreate(
            user=user,
            credential_id=bytes_to_base64url(verification.credential_id),
            public_key=bytes(verification.credential_public_key),
            sign_count=verification.sign_count,
            user_handle=bytes_to_base64url(str(user.id).encode()),
        )

    @classmethod
    async def generate_login_options(cls) -> LoginOptionsSchema:
        options = generate_authentication_options(
            rp_id=settings.WEBAUTHN_RP_ID,
            allow_credentials=[],  # discoverable — no allowCredentials
            user_verification=UserVerificationRequirement.REQUIRED,
        )
        await WebAuthnChallenge.objects.acreate(
            challenge=bytes_to_base64url(options.challenge),
            user=None,
            expires_at=timezone.now() + timedelta(seconds=WebAuthnChallenge.CHALLENGE_TTL_SECONDS),
        )
        return LoginOptionsSchema(**json.loads(options_to_json(options)))

    @classmethod
    async def verify_login(cls, data: LoginVerifyInput) -> User:
        client_data: ClientDataType = json.loads(
            base64url_to_bytes(data.response.clientDataJSON).decode()
        )
        challenge_value = client_data['challenge']

        challenge_obj = await WebAuthnChallenge.objects.filter(
            challenge=challenge_value,
            user=None,
        ).afirst()

        if not challenge_obj or challenge_obj.is_expired():
            raise RestAPIException(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                error_code='invalid_challenge',
                message='Challenge not found or expired',
            )

        credential_id_b64 = bytes_to_base64url(base64url_to_bytes(data.rawId))
        stored_credential = await WebAuthnCredential.objects.filter(
            credential_id=credential_id_b64,
        ).select_related('user').afirst()

        if not stored_credential:
            raise RestAPIException(
                status_code=StatusCode.HTTP_401_UNAUTHORIZED,
                error_code='credential_not_found',
                message='No registered passkey found for this device',
            )

        try:
            credential = AuthenticationCredential(
                id=data.id,
                raw_id=base64url_to_bytes(data.rawId),
                response=AuthenticatorAssertionResponse(
                    client_data_json=base64url_to_bytes(data.response.clientDataJSON),
                    authenticator_data=base64url_to_bytes(data.response.authenticatorData),
                    signature=base64url_to_bytes(data.response.signature),
                    user_handle=base64url_to_bytes(data.response.userHandle) if data.response.userHandle else None,
                ),
            )
            verification = verify_authentication_response(
                credential=credential,
                expected_challenge=base64url_to_bytes(challenge_value),
                expected_rp_id=settings.WEBAUTHN_RP_ID,
                expected_origin=settings.WEBAUTHN_ORIGIN,
                credential_public_key=bytes(stored_credential.public_key),
                credential_current_sign_count=stored_credential.sign_count,
                require_user_verification=True,
            )
        except Exception as exc:
            raise RestAPIException(
                status_code=StatusCode.HTTP_401_UNAUTHORIZED,
                error_code='verification_failed',
                message=f'Authentication verification failed: {exc}',
            )

        if data.response.userHandle:
            expected_handle = bytes_to_base64url(str(stored_credential.user_id).encode())
            if data.response.userHandle != expected_handle:
                raise RestAPIException(
                    status_code=StatusCode.HTTP_401_UNAUTHORIZED,
                    error_code='user_handle_mismatch',
                    message='User handle mismatch',
                )

        await challenge_obj.adelete()

        stored_credential.sign_count = verification.new_sign_count
        await stored_credential.asave(update_fields=['sign_count'])

        return stored_credential.user

    @classmethod
    async def get_credentials(cls, user: User) -> CredentialsSchema:
        credentials = await sync_to_async(list)(
            WebAuthnCredential.objects.filter(user=user).order_by('-created_at')
        )
        credential_infos = [
            WebAuthnCredentialInfo(
                id=c.id,
                credential_id=c.credential_id,
                created_at=TimeUtils.to_default_str(c.created_at),
            )
            for c in credentials
        ]
        return CredentialsSchema(
            has_passkey=len(credentials) > 0,
            credentials=credential_infos,
        )

    @classmethod
    async def delete_credential(cls, user: User, credential_id: str) -> None:
        deleted_count, _ = await WebAuthnCredential.objects.filter(
            user=user,
            credential_id=credential_id,
        ).adelete()
        if deleted_count == 0:
            raise RestAPIException(
                status_code=StatusCode.HTTP_404_NOT_FOUND,
                error_code='credential_not_found',
                message='Credential not found',
            )
