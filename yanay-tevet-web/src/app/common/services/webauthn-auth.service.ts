import {Injectable} from '@angular/core';
import {
    webAuthnCredentialsView,
    webAuthnDeleteCredentialView,
    webAuthnLoginOptionsView,
    webAuthnLoginVerifyView,
    webAuthnRegisterOptionsView,
    webAuthnRegisterVerifyView,
} from '../../../generated-files/auth';
import type {
    AuthSchema,
    CredentialsSchema,
    LoginOptionsSchema,
    LoginVerifyInput,
    RegistrationOptionsSchema,
    RegistrationVerifyInput,
} from '../../../generated-files/auth';

interface WebAuthnUser {
    id: string;
    name: string;
    displayName: string;
}

interface ExcludeCredential {
    id: string;
    type: string;
    transports?: string[];
}

@Injectable({
    providedIn: 'root'
})
export class WebAuthnAuthService {

    async isPasskeySupported(): Promise<boolean> {
        if (!window.PublicKeyCredential) {
            return false;
        }
        return PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable();
    }

    async getCredentials(): Promise<CredentialsSchema> {
        const {data} = await webAuthnCredentialsView();
        return data!;
    }

    async deleteCredential(credentialId: string): Promise<void> {
        await webAuthnDeleteCredentialView({body: {credential_id: credentialId}});
    }

    async registerPasskey(): Promise<AuthSchema> {
        const options = await this.getRegisterOptions();
        const credential = await this.createCredential(options);
        return this.verifyRegistration(credential);
    }

    async loginWithPasskey(): Promise<AuthSchema> {
        const options = await this.getLoginOptions();
        const credential = await this.getAssertion(options);
        return this.verifyLogin(credential);
    }

    private async getRegisterOptions(): Promise<RegistrationOptionsSchema> {
        const {data, error} = await webAuthnRegisterOptionsView();
        if (error) {
            throw error;
        }
        return data!;
    }

    private async verifyRegistration(credential: RegistrationVerifyInput): Promise<AuthSchema> {
        const {data, error} = await webAuthnRegisterVerifyView({body: credential});
        if (error) {
            throw error;
        }
        return data!;
    }

    private async getLoginOptions(): Promise<LoginOptionsSchema> {
        const {data, error} = await webAuthnLoginOptionsView();
        if (error) {
            throw error;
        }
        return data!;
    }

    private async verifyLogin(credential: LoginVerifyInput): Promise<AuthSchema> {
        const {data, error} = await webAuthnLoginVerifyView({body: credential});
        if (error) {
            throw error;
        }
        return data!;
    }

    private async createCredential(options: RegistrationOptionsSchema): Promise<RegistrationVerifyInput> {
        const user = options.user as unknown as WebAuthnUser;
        const creationOptions: PublicKeyCredentialCreationOptions = {
            challenge: this.base64urlToUint8Array(options.challenge),
            rp: options.rp as unknown as PublicKeyCredentialRpEntity,
            user: {
                id: this.base64urlToUint8Array(user.id),
                name: user.name,
                displayName: user.displayName,
            },
            pubKeyCredParams: options.pubKeyCredParams as unknown as PublicKeyCredentialParameters[],
            timeout: options.timeout ?? undefined,
            attestation: (options.attestation ?? 'none') as AttestationConveyancePreference,
            authenticatorSelection: options.authenticatorSelection as unknown as AuthenticatorSelectionCriteria,
            excludeCredentials: (options.excludeCredentials ?? []).map(c => {
                const cred = c as unknown as ExcludeCredential;
                return {
                    id: this.base64urlToUint8Array(cred.id),
                    type: cred.type as PublicKeyCredentialType,
                    transports: (cred.transports ?? []) as AuthenticatorTransport[],
                };
            }),
        };

        const credential = await navigator.credentials.create({publicKey: creationOptions}) as PublicKeyCredential;
        if (!credential) {
            throw new Error('Passkey creation was cancelled or failed');
        }

        const response = credential.response as AuthenticatorAttestationResponse;
        return {
            id: credential.id,
            rawId: this.arrayBufferToBase64url(credential.rawId),
            type: credential.type,
            response: {
                clientDataJSON: this.arrayBufferToBase64url(response.clientDataJSON),
                attestationObject: this.arrayBufferToBase64url(response.attestationObject),
                transports: response.getTransports ? response.getTransports() : [],
            },
        };
    }

    private async getAssertion(options: LoginOptionsSchema): Promise<LoginVerifyInput> {
        const requestOptions: PublicKeyCredentialRequestOptions = {
            challenge: this.base64urlToUint8Array(options.challenge),
            rpId: options.rpId ?? undefined,
            allowCredentials: [],
            userVerification: (options.userVerification ?? 'required') as UserVerificationRequirement,
            timeout: options.timeout ?? undefined,
        };

        const credential = await navigator.credentials.get({publicKey: requestOptions}) as PublicKeyCredential;
        if (!credential) {
            throw new Error('Passkey authentication was cancelled or failed');
        }

        const response = credential.response as AuthenticatorAssertionResponse;
        return {
            id: credential.id,
            rawId: this.arrayBufferToBase64url(credential.rawId),
            type: credential.type,
            response: {
                clientDataJSON: this.arrayBufferToBase64url(response.clientDataJSON),
                authenticatorData: this.arrayBufferToBase64url(response.authenticatorData),
                signature: this.arrayBufferToBase64url(response.signature),
                userHandle: response.userHandle ? this.arrayBufferToBase64url(response.userHandle) : null,
            },
        };
    }

    private arrayBufferToBase64url(buffer: ArrayBuffer): string {
        const bytes = new Uint8Array(buffer);
        let binary = '';
        for (let i = 0; i < bytes.byteLength; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
    }

    private base64urlToUint8Array(base64url: string): Uint8Array<ArrayBuffer> {
        const base64 = base64url.replace(/-/g, '+').replace(/_/g, '/');
        const padded = base64.padEnd(base64.length + (4 - (base64.length % 4)) % 4, '=');
        const binary = atob(padded);
        const buffer = new ArrayBuffer(binary.length);
        const bytes = new Uint8Array(buffer);
        for (let i = 0; i < binary.length; i++) {
            bytes[i] = binary.charCodeAt(i);
        }
        return bytes;
    }
}
